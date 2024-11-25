from .views import *
from .rest_views import *
from django.urls import path


urlpatterns = [
    path('login', login, name='login'),
    path('profiles/boards/<int:board_id>/', get_profiles_by_board, name='get_profiles_by_board'),

    path('profiles/', get_profiles, name='get_profiles'),
    path('profiles/<int:profile_id>', get_profile_detail, name='get_profiles'),
    path('profiles/create', create_profile, name='create_profile')
]