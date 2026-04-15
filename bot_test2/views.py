import json

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Profile
from .services import fetch_all


def cors(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def json_response(data, status=200):
    return cors(JsonResponse(data, status=status))


def error_response(message, status):
    return json_response({'status': 'error', 'message': message}, status=status)


def serialize_profile(profile, full=True):
    data = {
        'id': profile.id,
        'name': profile.name,
        'gender': profile.gender,
        'age': profile.age,
        'age_group': profile.age_group,
        'country_id': profile.country_id,
    }
    if full:
        data['gender_probability'] = profile.gender_probability
        data['sample_size'] = profile.sample_size
        data['country_probability'] = profile.country_probability
        data['created_at'] = profile.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    return data


@method_decorator(csrf_exempt, name='dispatch')
class ProfileListView(View):

    def options(self, request, *args, **kwargs):
        return cors(JsonResponse({}, status=200))

    def post(self, request):
        # Parse body
        try:
            body = json.loads(request.body or '{}')
        except (json.JSONDecodeError, ValueError):
            return error_response('Invalid JSON body', 400)

        if not isinstance(body, dict):
            return error_response('Request body must be a JSON object', 422)

        name = body.get('name')

        if name is None or (isinstance(name, str) and name.strip() == ''):
            return error_response('name is required', 400)

        if not isinstance(name, str):
            return error_response('name must be a string', 422)

        name = name.strip().lower()

        # Idempotency: return existing profile if name already exists
        existing = Profile.objects.filter(name=name).first()
        if existing:
            return json_response({
                'status': 'success',
                'message': 'Profile already exists',
                'data': serialize_profile(existing, full=True),
            }, status=200)

        # Call external APIs
        try:
            api_data = fetch_all(name)
        except (ValueError, RuntimeError) as exc:
            return error_response(str(exc), 502)

        # Persist
        profile = Profile.objects.create(name=name, **api_data)

        return json_response({
            'status': 'success',
            'data': serialize_profile(profile, full=True),
        }, status=201)

    def get(self, request):
        qs = Profile.objects.all()

        gender = request.GET.get('gender')
        country_id = request.GET.get('country_id')
        age_group = request.GET.get('age_group')

        if gender:
            qs = qs.filter(gender__iexact=gender)
        if country_id:
            qs = qs.filter(country_id__iexact=country_id)
        if age_group:
            qs = qs.filter(age_group__iexact=age_group)

        profiles = list(qs)
        return json_response({
            'status': 'success',
            'count': len(profiles),
            'data': [serialize_profile(p, full=False) for p in profiles],
        })


@method_decorator(csrf_exempt, name='dispatch')
class ProfileDetailView(View):

    def options(self, request, *args, **kwargs):
        return cors(JsonResponse({}, status=200))

    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return error_response('Profile not found', 404)

        return json_response({
            'status': 'success',
            'data': serialize_profile(profile, full=True),
        })

    def delete(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return error_response('Profile not found', 404)

        profile.delete()
        response = JsonResponse({}, status=204)
        return cors(response)