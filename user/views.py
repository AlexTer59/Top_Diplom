from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model, authenticate
from django.contrib import messages
from user.forms import *


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