from django.urls import path
from .views import *


urlpatterns = [
    # ================ My boards views ==================
    path('boards/owned/', owned_boards, name='owned_boards'),
    path('boards/shared/', shared_boards, name='shared_boards'),
    path('boards/<int:board_id>/', detail_board, name='detail_board'),
    path('boards/<int:board_id>/edit/', edit_board, name='detail_board'),

    # ================ Default boards CRUD views ==================
    path('boards/create/', create_board, name='create_board'),
    path('boards/<int:board_id>/delete/', delete_board, name='delete_board'),

    # ================ My lists views ==================
    path('boards/<int:board_id>/lists/', get_lists_by_board, name='get_lists_by_board'),
    path('boards/<int:board_id>/lists/create/', create_list, name='board_create_list'),
    path('boards/<int:board_id>/lists/<int:list_id>/edit/', edit_list, name='board_edit_list'),
    path('boards/<int:board_id>/lists/<int:list_id>/delete/', delete_list, name='board_delete_list'),

    # ================ Default lists CRUD views ==================
    path('lists/create/', create_list, name='create_list'),
    path('lists/<int:list_id>/delete/', delete_list, name='delete_list'),

    # ================ My tasks views ==================
    path('lists/<int:list_id>/tasks/', get_tasks_by_list, name='get_tasks_by_list'),

    # ================ Default tasks CRUD views ==================
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/<int:task_id>/update/', update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),


]


