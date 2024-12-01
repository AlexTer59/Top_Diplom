# Generated by Django 5.1.3 on 2024-11-28 18:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_profile_user'),
    ]

    operations = [
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
