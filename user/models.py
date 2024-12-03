from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now
import os

# Create your models here.

def avatar_upload_path(instance, filename):
    """
    Формирует путь для сохранения аватара, используя username пользователя.
    """
    ext = filename.split('.')[-1]  # Получаем расширение файла
    filename = f"{instance.user.username}.{ext}"  # Формируем новое имя файла
    return os.path.join('avatars/', filename)  # Путь для сохранения


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Фамилия'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Удаляем старый файл, если аватар изменился
        if self.pk:  # Проверяем, существует ли объект
            old_avatar = Profile.objects.filter(pk=self.pk).first().avatar
            if old_avatar and old_avatar.name != self.avatar.name:
                old_avatar_path = old_avatar.path
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
        super().save(*args, **kwargs)


class Subscription(models.Model):
    BASE = 'base'
    PREMIUM = 'premium'

    TIER_CHOICES = [
        (BASE, 'Базовый'),
        (PREMIUM, 'Премиум'),
    ]

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Профиль пользователя'
    )
    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default=BASE,
        verbose_name='Тип подписки'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата истечения подписки'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания подписки'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата последнего обновления подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def is_active(self):
        """
        Проверяет, активна ли подписка.
        """
        return self.tier == self.PREMIUM and (self.expires_at is None or self.expires_at > now())

    def upgrade_to_premium(self, duration_days=30):
        if self.subscription_type == 'base':
            self.subscription_type = 'premium'
            self.expires_at = now() + timedelta(days=duration_days)
        elif self.subscription_type == 'premium':
            if self.expires_at and self.expires_at > now():
                # Продление активной подписки: прибавляем к дате окончания
                self.expires_at += timedelta(days=duration_days)
            else:
                # Если подписка истекла, начинаем с текущей даты
                self.expires_at = now() + timedelta(days=duration_days)
        self.save()

    def reset_to_base(self):
        self.subscription_type = 'base'
        self.expires_at = None
        self.save()

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.profile.user.username} -> {self.tier}'