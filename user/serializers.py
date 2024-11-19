from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # ID пользователя
    username = serializers.CharField(source='user.username', read_only=True)  # Имя пользователя
    avatar = serializers.ImageField(required=False, allow_null=True)  # Поле аватара
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # Поле "О себе"

