from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from core.models import Board, Task, List


def main(request):
    return render(request, 'main.html')

@login_required
def my_boards(request):
    """Страница досок пользователя"""
    # Получаем доски, которые создал пользователь
    owned_boards = Board.objects.filter(owner=request.user.profile)

    # Получаем доски, к которым пользователь был добавлен как участник
    shared_boards = Board.objects.filter(members=request.user.profile)

    context = {
        'owned_boards': owned_boards,
        'shared_boards': shared_boards,
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