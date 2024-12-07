from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from core.models import Board, Task, List
from django.views.generic import TemplateView

from user.models import Subscription
from user.serializers import *


def main(request):
    current_price = 499
    old_price = 599

    context = {
        'current_price': current_price,
        'old_price': old_price,

    }

    return render(request, 'main.html', context=context)

@login_required
def my_boards(request):
    """Страница досок пользователя"""
    profile = request.user.profile

    # Получаем доски, которые создал пользователь
    owned_boards = Board.objects.filter(owner=profile)

    # Получаем доски, к которым пользователь был добавлен как участник
    shared_boards = Board.objects.filter(members=profile)

    subscription = get_object_or_404(Subscription, profile=profile).tier
    print(subscription)

    context = {
        'owned_boards': owned_boards,
        'shared_boards': shared_boards,
        'is_base_sub': subscription == Subscription.BASE
    }

    return render(request, 'my_boards.html', context)

@login_required
def board_detail(request, board_id):
    """Детальная страница доски"""
    # Получаем доску по ID
    board = get_object_or_404(Board, id=board_id)

    # Получаем профиль текущего пользователя
    profile = request.user.profile

    # Проверяем, является ли пользователь владельцем или участником доски
    if board.owner != profile and not board.members.filter(id=profile.id).exists():
        raise PermissionDenied("У вас нет прав для просмотра этой доски.")

    # Отправляем данные доски в контекст
    context = {
        'board': board,
        'board_id': board_id
    }

    # Возвращаем страницу с деталями доски
    return render(request, 'board_detail.html', context)

@login_required
def task_detail(request, board_id, list_id, task_id):
    board = get_object_or_404(Board, id=board_id)
    task = get_object_or_404(Task, id=task_id)
    list = get_object_or_404(List, id=list_id)

    # Получаем профиль текущего пользователя
    profile = request.user.profile

    # Проверяем, является ли пользователь владельцем или участником доски
    if board.owner != profile and not board.members.filter(id=profile.id).exists():
        raise PermissionDenied("У вас нет прав для просмотра этой доски.")

    context = {
        'board': board,
        'board_id': board_id,
        'task': task,
        'task_id': task_id,
        'list': list,
        'list_id': list_id,
    }

    return render(request, 'task_detail.html', context)


class PricesDetailView(TemplateView):
    template_name = "price_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tiers'] = {
            'base': {
                'name': 'Базовый',
                'price': '0',
                'old_price': None,
                'features': [
                    'Доступ к базовым функциям',
                ],
                'disregards': [
                    'Отсутствуют диаграммы Ганта',
                    'До 4 человек в доске',
                    'Создание до 3 досок',
                ],
                'is_highlighted': False,
            },
            'premium': {
                'name': 'Премиум',
                'price': '499',
                'old_price': '599',
                'features': [
                    'Все базовые функции',
                    'Неограниченное количество досок',
                    'Диаграммы Ганта',
                    'Неограниченное количество участников в доске',
                ],
                'disregards': [
                ],
                'is_highlighted': False,
            },
        }
        return context