from django.urls import path
from .views import ProfileListView, ProfileDetailView
 
urlpatterns = [
    path('profiles', ProfileListView.as_view(), name='profiles-list'),
    path('profiles/', ProfileListView.as_view(), name='profiles-list-slash'),
    path('profiles/<str:profile_id>', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/<str:profile_id>/', ProfileDetailView.as_view(), name='profile-detail-slash'),
]
 