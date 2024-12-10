from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model, authenticate
from django.contrib import messages
from user.forms import *
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from core.models import *
from .models import *


def login(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                auth_login(request, user)
                messages.success(request, "Вы успешно вошли в систему!")
                return redirect('main')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('main')


def register(request):
    if request.method == 'POST':
        print(request.FILES)
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # Создание пользователя и профиля
            auth_login(request, user)  # Авторизация пользователя
            messages.success(request, "Вы успешно зарегистрированы!")
            return redirect('main')  # Перенаправление на главную страницу или любую другую
    else:
        form = RegistrationForm()

    return render(request, 'user/register.html', {'form': form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем профиль по ID из URL
        profile_id = self.kwargs.get('profile_id')
        user_profile = get_object_or_404(Profile, id=profile_id)

        # Проверяем, является ли текущий пользователь владельцем профиля
        is_owner = self.request.user.profile == user_profile

        # Личная информация
        context['profile'] = user_profile
        context['is_owner'] = is_owner

        if is_owner:
            # Мои доски (доски, где пользователь владелец или участник)
            boards = Board.objects.filter(
                Q(owner=user_profile) | Q(members=user_profile)
            ).distinct()

            # Мои задачи (все задачи, назначенные на пользователя)
            tasks = Task.objects.filter(assigned_to=user_profile).select_related('board', 'status')

            # Подсчитываем количество задач для каждой доски
            for board in boards:
                board.tasks_count = Task.objects.filter(board=board).count()

            context['boards'] = boards
            context['tasks'] = tasks
        else:
            # Если пользователь не владелец, не передаем доски и задачи
            context['boards'] = []
            context['tasks'] = []

        return context