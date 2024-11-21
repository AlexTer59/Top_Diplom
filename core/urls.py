

from django.contrib import admin
from django.urls import path
from .views import *
from .rest_views import *


urlpatterns = [
    path('', main, name='main'),
    path('test-board', board, name='board'),
    path('login', login, name='login'),

    path('boards/', list_boards, name='list_boards'),
    path('boards/create/', create_board, name='create_board'),
    path('boards/<int:board_id>/update/', update_board, name='update_board'),
    path('boards/<int:board_id>/delete/', delete_board, name='delete_board'),

    path('lists/', list_lists, name='list_lists'),
    path('lists/create/', create_list, name='create_list'),
    path('lists/<int:list_id>/update/', update_list, name='update_list'),
    path('lists/<int:list_id>/delete/', delete_list, name='delete_list'),

    path('tasks/', list_tasks, name='list_tasks'),
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/<int:task_id>/update/', update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),


]