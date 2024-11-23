from .views import *
from .rest_views import *
from django.urls import path


urlpatterns = [
    path('login', login, name='login'),

    path('profile/list', get_profiles, name='get_profiles'),
    path('profile/<int:profile_id>', get_profile_detail, name='get_profiles'),
    path('profile/create', create_profile, name='create_profile')
]