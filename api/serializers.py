from datetime import timedelta, datetime


from rest_framework import serializers
from django.utils.timezone import localtime
from django.db import models
from rest_framework.exceptions import ValidationError

from core.models import Board, List, Task, TaskNote, TaskNoteLike
from django.utils import timezone
from user.models import *
from user.serializers import *


class BoardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True)
    owner = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    members = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), many=True)

    def create(self, validated_data):
        members = validated_data.pop('members', [])

        # Создание доски
        board = Board.objects.create(**validated_data)
        board.members.set(members)

        # Создание дефолтных списков для новой доски
        default_lists = ['Задачи', 'Сегодня', 'В процессе', 'Выполнено', 'Архив']
        for list_name in default_lists:
            List.objects.create(board=board, name=list_name)
        return board

    def update(self, instance, validated_data):
        members = validated_data.pop('members', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.members.set(members)
        instance.save()
        return instance

    # Проверка общего количества досок для пользователя
    def validate(self, attrs):
        # Получаем текущего пользователя из контекста
        profile = self.context['request'].user.profile
        subscription = Subscription.objects.get(profile=profile)

        # Проверка на количество досок, если подписка базовая
        if subscription.tier == Subscription.BASE:
            board_count = Board.objects.filter(owner=profile).count()
            if board_count >= 3:
                raise ValidationError("Вы не можете создать больше 3 досок с базовой подпиской.")

        return attrs

    # Проверка на количество участников (не более 3)
    def validate_members(self, value):
        # Получаем текущего пользователя из контекста
        profile = self.context['request'].user.profile
        subscription = Subscription.objects.get(profile=profile)

        # Проверка количества участников для базовой подписки
        if subscription.tier == Subscription.BASE:
            if len(value) > 3:
                raise ValidationError("Вы можете выбрать не более 3 участников с базовой подпиской.")

        return value


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
    board_name = serializers.CharField(source='board.name', read_only=True)
    status = serializers.PrimaryKeyRelatedField(queryset=List.objects.all())
    status_name = serializers.CharField(source='status.name', read_only=True)
    is_urgent = serializers.BooleanField(default=False)
    is_overdue = serializers.BooleanField(default=False)
    due_date = serializers.DateField(required=False, allow_null=True, default=get_default_due_date)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_at_datetime = serializers.SerializerMethodField(read_only=True)
    updated_at_datetime = serializers.SerializerMethodField(read_only=True)
    labels = serializers.JSONField(required=False, default=dict)
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), required=False, allow_null=True)
    created_by_id = serializers.CharField(source='created_by.user.id', read_only=True)

    assigned_to_username = serializers.CharField(source='assigned_to.user.username', read_only=True)
    assigned_to_avatar = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.user.username', read_only=True)


    def validate(self, attrs):
        # Проверяем, если задача просрочена
        if 'due_date' in attrs and attrs['due_date'] and attrs['due_date'] < timezone.now().date():
            attrs['is_overdue'] = True
        return attrs

    def create(self, validated_data):
        # Получаем текущего пользователя через request
        created_by = self.context['request'].user.profile  # Получаем профиль текущего пользователя
        assigned_to_data = validated_data.pop('assigned_to', None)

        # Создаем задачу и передаем created_by
        task = Task.objects.create(created_by=created_by, **validated_data)

        if assigned_to_data:
            task.assigned_to = assigned_to_data
            task.save()

        task.check_overdue()

        return task

    def update(self, instance, validated_data):
        assigned_to_data = validated_data.pop('assigned_to', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if assigned_to_data:
            instance.assigned_to = assigned_to_data

        instance.save()

        instance.check_overdue()
        return instance

    def get_created_at_datetime(self, obj):
        return localtime(obj.created_at).strftime('%d-%m-%Y %H:%M')

    def get_updated_at_datetime(self, obj):
        return localtime(obj.updated_at).strftime('%d-%m-%Y %H:%M')

    def get_assigned_to_avatar(self, obj):
        if obj.assigned_to and obj.assigned_to.avatar:
            return obj.assigned_to.avatar.url
        return None

    def to_internal_value(self, data):
        # Если due_date отсутствует, не ставим дефолтную дату
        if 'due_date' not in data or data['due_date'] is None:
            data.pop('due_date', None)

        return super().to_internal_value(data)

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

        # Проверяем, не создается ли список с именем "Архив"
        if validated_data['name'].lower() == 'архив':
            raise serializers.ValidationError("Нельзя создать список с именем 'Архив'")

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
        instance.save()  # Сохраняем обновленные данные

        return instance

class TaskNoteSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    note = serializers.CharField(max_length=1024)
    profile = serializers.CharField(source='profile.user.username', read_only=True)
    created_at = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return localtime(obj.created_at).strftime('%d-%m-%Y %H:%M')

    def get_likes_count(self, obj):
        return obj.note_likes.count()

    def get_is_liked(self, obj):
        profile = self.context['request'].user.profile
        return TaskNoteLike.objects.filter(profile=profile, note=obj).exists()

    def create(self, validated_data):
        return TaskNote.objects.create(**validated_data)