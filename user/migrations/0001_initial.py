# Generated by Django 5.1.3 on 2024-12-09 23:35

import django.db.models.deletion
import user.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=user.models.avatar_upload_path, verbose_name='Аватар')),
                ('bio', models.TextField(blank=True, null=True, verbose_name='О себе')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Фамилия')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier', models.CharField(choices=[('base', 'Базовый'), ('premium', 'Премиум')], default='base', max_length=20, verbose_name='Тип подписки')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата истечения подписки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания подписки')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата последнего обновления подписки')),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='user.profile', verbose_name='Профиль пользователя')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
    ]
