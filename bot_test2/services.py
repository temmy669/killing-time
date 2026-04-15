import urllib.request
import urllib.error
import json


GENDERIZE_URL = 'https://api.genderize.io?name={name}'
AGIFY_URL = 'https://api.agify.io?name={name}'
NATIONALIZE_URL = 'https://api.nationalize.io?name={name}'


def _fetch(url: str) -> dict:
    """Fetch JSON from a URL. Raises urllib.error.URLError on network failure."""
    req = urllib.request.Request(url, headers={'User-Agent': 'nameprofile/1.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def classify_age_group(age: int) -> str:
    if age <= 12:
        return 'child'
    elif age <= 19:
        return 'teenager'
    elif age <= 59:
        return 'adult'
    return 'senior'


def fetch_all(name: str) -> dict:
    """
    Call all three external APIs and return a merged, classified result dict.
    Raises ValueError with a descriptive message on invalid/missing data (→ 502).
    Raises RuntimeError on network/upstream failure (→ 502).
    """
    name_enc = urllib.parse.quote(name.strip().lower())

    # --- Genderize ---
    try:
        g = _fetch(GENDERIZE_URL.format(name=name_enc))
    except Exception:
        raise RuntimeError('Genderize returned an invalid response')

    if not g.get('gender') or g.get('count', 0) == 0:
        raise ValueError('Genderize returned an invalid response')

    # --- Agify ---
    try:
        a = _fetch(AGIFY_URL.format(name=name_enc))
    except Exception:
        raise RuntimeError('Agify returned an invalid response')

    if a.get('age') is None:
        raise ValueError('Agify returned an invalid response')

    # --- Nationalize ---
    try:
        n = _fetch(NATIONALIZE_URL.format(name=name_enc))
    except Exception:
        raise RuntimeError('Nationalize returned an invalid response')

    countries = n.get('country') or []
    if not countries:
        raise ValueError('Nationalize returned an invalid response')

    top_country = max(countries, key=lambda c: c.get('probability', 0))

    return {
        'gender': g['gender'],
        'gender_probability': g.get('probability'),
        'sample_size': g.get('count'),
        'age': a['age'],
        'age_group': classify_age_group(a['age']),
        'country_id': top_country.get('country_id'),
        'country_probability': top_country.get('probability'),
    }


# Needed for URL encoding in fetch_all
import urllib.parse