from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from core.models import *


def check_board_access(profile, board_instance, permission_type):
    """
    Проверяет права доступа к доске.

    :param profile: Профиль пользователя.
    :param board_instance: Объект доски.
    :param permission_type: Тип операции ("C", "R", "U", "D").
    :raises PermissionDenied: Если доступ запрещен.
    """

    if permission_type not in ("C", "R", "U", "D"):
        raise ValueError("Недопустимый тип операции. Используйте 'C', 'R', 'U' или 'D'.")

    if isinstance(board_instance, Board):  # При создании списка передается объект доски
        board = board_instance
    else:
        raise ValueError("board_instance должен быть объектом Board.")

    if board_instance.owner == profile:
        # Создатель доски имеет полный доступ
        return

    if profile in board_instance.members.all():
        # Участники доски имеют только R-доступ
        if permission_type != "R":
            raise PermissionDenied("У вас нет прав на выполнение этой операции с доской.")
        return

    # Остальные пользователи не имеют доступа
    raise PermissionDenied("У вас нет доступа к этой доске.")


def check_list_access(profile, board_or_list, permission_type):
    """
    Проверяет права доступа к списку.

    :param profile: Профиль пользователя.
    :param board_or_list: Объект списка или доски (при создании списка).
    :param permission_type: Тип операции ("C", "R", "U", "D").
    :raises PermissionDenied: Если доступ запрещен.
    """
    if permission_type not in ("C", "R", "U", "D"):
        raise ValueError("Недопустимый тип операции. Используйте 'C', 'R', 'U' или 'D'.")

    if isinstance(board_or_list, List):
        board = board_or_list.board
    elif isinstance(board_or_list, Board):  # При создании списка передается объект доски
        board = board_or_list
    else:
        raise ValueError("list_or_task должен быть объектом Board или List.")

    if board.owner == profile:
        # Создатель доски имеет полный доступ
        return

    if profile in board.members.all():
        # Участники могут только читать (R) список
        if permission_type == "R":
            return
        elif permission_type in ("U", "C", "D"):
            # Участник не может изменять (обновлять), создавать или удалять список
            raise PermissionDenied("У вас нет прав на выполнение этой операции с этим списком.")

    # Остальные пользователи не имеют доступа
    raise PermissionDenied("У вас нет доступа к этому списку.")


def check_task_access(profile, task, permission_type):
    """
    Проверяет права доступа к задаче.

    :param profile: Профиль пользователя.
    :param task: Объект задачи.
    :param permission_type: Тип операции ("C", "R", "U", "D").
    :raises PermissionDenied: Если доступ запрещен.
    """
    if permission_type not in ("C", "R", "U", "D"):
        raise ValueError("Недопустимый тип операции. Используйте 'C', 'R', 'U' или 'D'.")

    # Извлекаем доску
    board = task.board

    # Полный доступ у создателя доски
    if board.owner == profile:
        return

    # Проверка прав для участников доски
    if profile in board.members.all():
        if permission_type == "R":
            return  # Участник может читать все задачи

        if permission_type == "U" or permission_type == "D":
            # Участник может редактировать или удалять только свои задачи
            if task.assigned_to == profile or task.created_by == profile:
                return  # Участник может редактировать или удалять свою задачу
            raise PermissionDenied("Вы не можете редактировать или удалять чужие задачи.")

        # Статус можно менять как для задач, так и для тех, что поставлены участнику
        if permission_type == "U" and task.assigned_to == profile:
            return

    raise PermissionDenied("У вас нет доступа к этой задаче.")
