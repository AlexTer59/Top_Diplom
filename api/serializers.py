from datetime import timedelta, datetime

from rest_framework import serializers
from django.utils.timezone import localtime
from django.db import models
from core.models import Board, List, Task
from django.utils import timezone
from user.models import Profile
from user.serializers import *


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
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


def get_default_due_date():
    return (timezone.now() + timedelta(days=7)).date()

class TaskSerializer(serializers.Serializer):
    STATUS_IN_PROGRESS = Task.STATUS_IN_PROGRESS
    STATUS_URGENT = Task.STATUS_URGENT
    STATUS_OVERDUE = Task.STATUS_OVERDUE
    STATUS_COMPLETED = Task.STATUS_COMPLETED

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    list = serializers.PrimaryKeyRelatedField(queryset=List.objects.all())
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
    due_date = serializers.DateField(required=False, allow_null=True, default=get_default_due_date)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    labels = serializers.JSONField(required=False, default=dict)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), required=False, allow_null=True)

    assigned_to_username = serializers.CharField(source='assigned_to.user.username', read_only=True)
    assigned_to_avatar = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.user.username', read_only=True)


    def get_assigned_to_avatar(self, obj):
        if obj.assigned_to and obj.assigned_to.avatar:
            return obj.assigned_to.avatar.url
        return None

    def to_internal_value(self, data):
        # Если due_date отсутствует или равно null, назначаем дефолтное значение
        if 'due_date' not in data or data['due_date'] is None:
            data['due_date'] = get_default_due_date()

        return super().to_internal_value(data)


    def create(self, validated_data):
        # Получаем текущего пользователя через request
        created_by = self.context['request'].user.profile  # Получаем профиль текущего пользователя
        assigned_to_data = validated_data.pop('assigned_to', None)

        # Создаем задачу и передаем created_by
        task = Task.objects.create(created_by=created_by, **validated_data)

        if assigned_to_data:
            task.assigned_to = assigned_to_data  # Это теперь объект Profile
            task.save()

        return task

    def update(self, instance, validated_data):
        assigned_to_data = validated_data.pop('assigned_to', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if assigned_to_data:
            instance.assigned_to = assigned_to_data  # Это теперь объект Profile

        instance.save()
        return instance


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    board = serializers.IntegerField(source='board.id')  # ID доски
    position = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        # Получаем board_id из validated_data
        board_id = validated_data['board'].id

        # Получаем доску
        board = Board.objects.get(id=board_id)

        # Вычисляем максимальную позицию для этой доски
        max_position = List.objects.filter(board=board).aggregate(models.Max('position'))['position__max'] or 0
        validated_data['position'] = max_position + 1  # Увеличиваем на 1

        # Создаем новый список с вычисленной позицией
        list_instance = List.objects.create(
            board=board,
            name=validated_data['name'],
            position=validated_data['position'],
        )
        return list_instance

    def update(self, instance, validated_data):
        # Обновляем только разрешенные поля
        instance.name = validated_data.get('name', instance.name)

        # Важное замечание: не изменяем 'position' по умолчанию, если только не требуется изменить порядок
        # instance.position = validated_data.get('position', instance.position)  # Если хотите изменить position, раскомментируйте

        instance.save()  # Сохраняем обновленные данные

        return instance
