from .views import *
from .rest_views import *
from django.urls import path


urlpatterns = [
    path('profiles/login', login, name='login'),
    path('profiles/logout', logout, name='logout'),
    path('profiles/register', register, name='register'),
    path('profiles/<int:profile_id>', ProfileView.as_view(), name='profile_detail'),

    path('profiles/boards/<int:board_id>/', get_profiles_by_board, name='get_profiles_by_board'),

    path('profiles/', get_profiles, name='get_profiles'),
    path('profiles/<int:profile_id>/api/', get_profile_detail, name='get_profile_detail'),
    path('profiles/<int:profile_id>/api/edit/', edit_profile, name='edit_profile'),
    path('profiles/subscription/get/api/', get_subscription, name='get_subscription')
]