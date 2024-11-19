from django.contrib import admin
from django.db import router
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


# Создаём роутер
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'lists', ListViewSet, basename='list')
router.register(r'tasks', TaskViewSet, basename='task')


urlpatterns = [
    path('', include(router.urls)),
]