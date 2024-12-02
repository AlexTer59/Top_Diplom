

from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('', main, name='main'),
    path('boards/', my_boards, name='boards'),
    path('boards/<int:board_id>/', board_detail, name='board_detail'),
    path('boards/<int:board_id>/lists/<int:list_id>/tasks/<int:task_id>/', task_detail, name='task_detail'),
    path('prices/', PricesDetailView.as_view(), name='prices_detail')

]