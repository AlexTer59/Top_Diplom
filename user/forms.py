from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model

from user.models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'}),
        label="Имя пользователя"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
        label="Пароль"
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)  # Вызов родительского конструктора

    def get_user(self):
        return self.user

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')  # Имя пользователя
        password = cleaned_data.get('password')  # Пароль

        self.user = authenticate(self.request, username=username, password=password)

        if not self.user:
            raise ValidationError('Неверное имя пользователя или пароль.')
        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
        label="Имя пользователя"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
        label="Email"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        label="Пароль"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}),
        label="Повторите пароль"
    )
    avatar = forms.ImageField(required=False, label='Аватарка')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError("Пароли не совпадают")

        try:
            validate_password(password1)  # Проверка пароля
        except ValidationError as e:
            raise ValidationError(e.messages)

        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует!")

        return username

    def save(self):
        # Создание пользователя
        user = get_user_model().objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )
        print(self.cleaned_data['avatar'])
        # Создание профиля
        Profile.objects.create(
            user=user,
            avatar=self.cleaned_data.get('avatar', None),
            bio='',  # Можно оставить пустым или добавить текст
        )

        return user