

from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('', main, name='main'),
    path('boards/', my_boards, name='boards'),
    path('boards/<int:board_id>/', board_detail, name='board_detail'),

]