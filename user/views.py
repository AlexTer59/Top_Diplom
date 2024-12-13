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

        # Подписка
        subscription = getattr(user_profile, 'subscription', None)
        if subscription:
            context['subscription_type'] = subscription.get_tier_display()
            context['subscription_expiration'] = subscription.expires_at or "—"
        else:
            context['subscription_type'] = "Базовая"
            context['subscription_expiration'] = "—"

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

            # Сортируем задачи
            tasks = sorted(
                tasks,
                key=lambda task: (
                    not task.is_overdue,  # Сначала просроченные задачи
                    not task.is_urgent,  # Затем срочные задачи
                    task.due_date  # И затем все задачи по дедлайну
                )
            )


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

@login_required
def activate_premium(request, profile_id):
    try:
        profile = request.user.profile
        subscription, created = Subscription.objects.get_or_create(profile=profile)

        if subscription.tier == Subscription.PREMIUM:
            if subscription.expires_at and subscription.expires_at > now():
                subscription.expires_at += timedelta(days=30)  # Продление подписки
            else:
                subscription.expires_at = now() + timedelta(days=30)  # Новая подписка
        else:
            subscription.tier = Subscription.PREMIUM
            subscription.expires_at = now() + timedelta(days=30)  # Новая подписка

        subscription.save()

        messages.success(request, "Премиум подписка активирована или продлена на 30 дней.")
        return redirect("profile_detail", profile_id=profile.id)  # Переход в профиль пользователя

    except Exception as e:
        messages.error(request, f"Ошибка активации подписки: {str(e)}")
        return redirect("price_detail.html")