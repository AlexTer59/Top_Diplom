from django.db import models
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
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
        ordering = ['position']  # Сортируем списки по полю position

    def save(self, *args, **kwargs):
        # Если это столбец "Архив", он должен быть всегда в конце
        if self.name == "Архив":
            # Получаем максимальную позицию всех списков, кроме "Архива"
            max_position = \
            List.objects.filter(board=self.board).exclude(name="Архив").aggregate(models.Max('position'))[
                'position__max'] or 0
            self.position = max_position + 1
        else:
            # Если это не "Архив", присваиваем максимальную позицию всех остальных списков + 1
            max_position = \
            List.objects.filter(board=self.board).exclude(name="Архив").aggregate(models.Max('position'))[
                'position__max'] or 0
            self.position = max_position + 1

            # Сдвигаем все остальные списки после текущего списка
            List.objects.filter(board=self.board, position__gte=self.position).update(position=models.F('position') + 1)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Task(models.Model):
    # Используем переменные для статусов
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_URGENT = 'urgent'
    STATUS_OVERDUE = 'overdue'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_URGENT, 'Срочно'),
        (STATUS_OVERDUE, 'Просрочено'),
        (STATUS_COMPLETED, 'Выполнено'),
    )

    title = models.CharField(max_length=255,
                             verbose_name="Название задачи")
    description = models.TextField(blank=True,
                                   null=True,
                                   verbose_name="Описание")
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='board_tasks',
                              verbose_name='Доска')
    status = models.ForeignKey(List,
                             on_delete=models.CASCADE,
                             related_name='list_tasks',
                             verbose_name="Статус")
    is_urgent = models.BooleanField(default=False)

    is_overdue = models.BooleanField(default=False)

    due_date = models.DateField(blank=True,
                                null=True,
                                default=timezone.now() + timedelta(weeks=1),
                                verbose_name="Срок выполнения"
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания",
                                      )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")
    labels = models.JSONField(default=dict,
                              blank=True,
                              verbose_name="Метки")
    created_by = models.ForeignKey(Profile,
                                   on_delete=models.CASCADE,
                                   related_name="created_tasks",
                                   verbose_name="Назначивший",)

    assigned_to = models.ForeignKey(Profile,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    related_name='tasks',
                                    verbose_name='Исполнитель')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def check_overdue(self):
        # Если дата дедлайна существует, проверяем её
        if self.due_date:
            if self.due_date < timezone.now().date():
                self.is_overdue = True
            else:
                self.is_overdue = False
            self.save(update_fields=['is_overdue'])


    def __str__(self):
        return self.title


class TaskComment(models.Model):
    comment = models.TextField(max_length=1024, verbose_name='Комментарий')
    task = models.ForeignKey(Task,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Задача')
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile,
                                related_name='profile_comments',
                                on_delete=models.CASCADE,
                                verbose_name='Профиль')

    def __str__(self):
        return f'{self.comment[:15]}...'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class TaskCommentLike(models.Model):
    comment = models.ForeignKey(TaskComment,
                             on_delete=models.CASCADE,
                             related_name='comment_likes',
                             )
    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE,
                                related_name='profile_likes')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.profile.user.username} лайкнул заметку "{self.comment.comment[:20]}..."'

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'




