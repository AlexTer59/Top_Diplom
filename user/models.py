from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile',
                                verbose_name='Пользователь')
    avatar = models.ImageField(upload_to='avatars/',
                               blank=True,
                               null=True,
                               verbose_name="Аватар")
    bio = models.TextField(blank=True,
                           null=True,
                           verbose_name='О себе')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.username



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
        return self.expires_at is None or self.expires_at > now()

    def can_downgrade(self):
        """
        Проверяет, можно ли переключиться с премиума на стандарт.
        """
        if self.tier == self.PREMIUM and self.expires_at and self.expires_at > now():
            return False  # Премиум активен, переключение запрещено
        return True

    def activate_premium(self, duration_days=30):
        """
        Активирует или продлевает премиум подписку.
        """
        self.tier = self.PREMIUM
        if self.expires_at and self.expires_at > now():
            self.expires_at += timedelta(days=duration_days)
        else:
            self.expires_at = now() + timedelta(days=duration_days)
        self.save()

    def activate_base(self):
        """
        Активирует базовую подписку, если это возможно.
        """
        if self.can_downgrade():
            self.tier = self.BASE
            self.expires_at = None
            self.save()
        else:
            raise ValueError("Нельзя переключиться на базовый тариф, пока активен премиум.")
