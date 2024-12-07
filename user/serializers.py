from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from user.models import Profile

class SubscriptionSerializer(serializers.Serializer):
    tier = serializers.CharField()
    expires_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ID профиля
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    birth_date = serializers.DateField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)

    def update(self, instance, validated_data):
        # Обновляем данные пользователя, только email
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
        instance.user.save()

        # Обновляем данные профиля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

