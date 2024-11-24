from django.db import models
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from user.models import Profile


class Board(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название доски")
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")
    owner = models.ForeignKey(Profile,
                              on_delete=models.CASCADE,
                              related_name="owned_boards",
                              verbose_name="Владелец")
    members = models.ManyToManyField(Profile,
                                     related_name="shared_boards",
                                     verbose_name="Участники",
                                     blank=True)

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def __str__(self):
        return self.name

class List(models.Model):
    name = models.CharField(max_length=255,
                            verbose_name="Название списка")
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='lists',
                              verbose_name="Доска")
    position = models.PositiveIntegerField(default=0,
                                           verbose_name="Позиция")

    class Meta:
        verbose_name = 'Список'
        verbose_name_plural = 'Списки'

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255,
                             verbose_name="Название задачи")
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name="Описание")
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='board_tasks',
                              verbose_name='Доска')
    list = models.ForeignKey(List,
                             on_delete=models.CASCADE,
                             related_name='list_tasks',
                             verbose_name="Список")
    position = models.PositiveIntegerField(default=0, verbose_name="Позиция")
    due_date = models.DateTimeField(blank=True,
                                    null=True,
                                    default=timezone.now() + timedelta(weeks=1),
                                    verbose_name="Срок выполнения")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")
    labels = models.JSONField(default=dict,
                              blank=True,
                              verbose_name="Метки")
    assigned_to = models.ForeignKey(Profile,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    related_name='tasks',
                                    verbose_name='Исполнитель')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


    def __str__(self):
        return self.title







