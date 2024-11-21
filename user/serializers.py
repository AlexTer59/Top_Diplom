from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from user.models import Profile


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value):
        """
        Валидация пароля с использованием стандартных валидаторов Django
        """
        validate_password(value)
        return value

    def validate_username(self, value):
        """
        Проверка уникальности username.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Этот username уже занят.")
        return value

    def create(self, validated_data):
        # Создаем пользователя с паролем
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer()  # Вставляем сериализатор для пользователя
    avatar = serializers.ImageField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        # Извлекаем данные пользователя из сериализатора
        user_data = validated_data.pop('user')

        # Создаем пользователя
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Создаем профиль с использованием оставшихся данных
        profile = Profile.objects.create(user=user, **validated_data)
        return profile