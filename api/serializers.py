from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils.timezone import localtime

from core.models import Board, List, Task
from user.models import Profile
from user.serializers import *


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True)
    owner = ProfileSerializer()
    members = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), many=True)

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board

    def update(self, instance, validated_data):
        members = validated_data.pop('members', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.members.set(members)
        instance.save()
        return instance

class TaskSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True)
    board = serializers.IntegerField(source='board.id')  # Ссылаемся на ID доски
    list = serializers.IntegerField(source='list.id')  # Ссылаемся на ID списка
    position = serializers.IntegerField(default=0)
    # due_date = serializers.DateTimeField(required=False, allow_null=True)
    due_date = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    labels = serializers.JSONField(required=False, default=dict)
    assigned_to = ProfileSerializer()  # Сериализуем объект Profile

    def get_due_date(self, obj):
        return localtime(obj.due_date).strftime('%d-%m-%Y %H:%M')

    def create(self, validated_data):
        # Создаем задачу
        assigned_to_data = validated_data.pop('assigned_to', None)
        task = Task.objects.create(**validated_data)

        # Если есть данные о пользователе, то привязываем к задаче
        if assigned_to_data:
            profile = Profile.objects.get(id=assigned_to_data['id'])
            task.assigned_to = profile
            task.save()

        return task

    def update(self, instance, validated_data):
        # Обновляем задачу
        assigned_to_data = validated_data.pop('assigned_to', None)

        # Обновляем поля задачи
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Если есть данные о пользователе, обновляем исполнителя
        if assigned_to_data:
            profile = Profile.objects.get(id=assigned_to_data['id'])
            instance.assigned_to = profile

        instance.save()
        return instance


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    board = serializers.IntegerField(source='board.id')  # ID доски
    position = serializers.IntegerField(validators=[UniqueValidator
                                                    (queryset=List.objects.all())])


