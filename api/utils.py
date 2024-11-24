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


def check_task_access(profile, list_or_task, permission_type):
    """
    Проверяет права доступа к задаче или возможной задаче.

    :param profile: Профиль пользователя.
    :param list_or_task: Объект задачи или списка (при создании задачи).
    :param permission_type: Тип операции ("C", "R", "U", "D").
    :raises PermissionDenied: Если доступ запрещен.
    """
    if permission_type not in ("C", "R", "U", "D"):
        raise ValueError("Недопустимый тип операции. Используйте 'C', 'R', 'U' или 'D'.")

    # Извлекаем доску
    if isinstance(list_or_task, Task):
        board = list_or_task.board
        task = list_or_task
    elif isinstance(list_or_task, List):
        board = list_or_task.board
        task = None
    else:
        raise ValueError("list_or_task должен быть объектом List или Task.")

    # Полный доступ у создателя доски
    if board.owner == profile:
        return

    # Проверка прав для участников доски
    if profile in board.members.all():
        if permission_type in ("R", "C"):
            # Участник может читать любые задачи и создавать задачи
            return

        if task:  # Для операций "U" или "D" с задачами
            if task.assigned_to == profile:
                return  # Участник может изменять или удалять только свои задачи

            raise PermissionDenied("Вы не можете изменять или удалять чужие задачи.")

    # Если пользователь не участник и не владелец, доступ запрещен
    raise PermissionDenied("У вас нет доступа к этой задаче.")
