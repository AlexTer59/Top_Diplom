from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from user.models import Profile



class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ID профиля
    username = serializers.CharField(source='user.username')  # Получение username из связанного user
    email = serializers.EmailField(source='user.email')  # Получение email из связанного user

    # Если есть дополнительные поля, например, bio или avatar
    bio = serializers.CharField(required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)

    def validate_user(self, value):
        """
        Проверка, что пользователь с указанным ID существует.
        """
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"Пользователь с ID {value} не найден.")
        # Сохраняем объект пользователя для дальнейшего использования
        self.user_instance = user
        return value

    def create(self, validated_data):
        """
        Создание профиля с использованием существующего пользователя.
        """
        # Используем сохраненный объект пользователя
        user = self.user_instance
        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        """
        Обновление профиля.
        """
        if 'user' in validated_data:
            # Используем сохраненный объект пользователя
            instance.user = self.user_instance
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance