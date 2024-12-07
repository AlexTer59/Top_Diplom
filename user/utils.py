from rest_framework.exceptions import PermissionDenied
from core.models import *
from .models import *

def check_profile_access(current_profile, profile_instance, permission_type):
    """
    Проверяет права доступа к доске.

    :param current_profile: Профиль пользователя.
    :param profile_instance: Объект доски.
    :param permission_type: Тип операции ("C", "R", "U", "D").
    :raises PermissionDenied: Если доступ запрещен.
    """

    if permission_type not in ("C", "R", "U", "D"):
        raise ValueError("Недопустимый тип операции. Используйте 'C', 'R', 'U' или 'D'.")

    if not isinstance(profile_instance, Profile):
        raise ValueError("profile_instance должен быть объектом Profile.")

    if permission_type == 'R':
        return

    if current_profile != profile_instance:
        raise PermissionDenied("У вас нет прав для выполнения этой операции с профилем.")

    # Если проверка прошла, доступ разрешен
    return

def check_subscription_access(current_profile, profile_instance, permission_type):

    if permission_type not in ("C", "R", "U", "D"):
        raise ValueError("Недопустимый тип операции. Используйте 'C', 'R', 'U' или 'D'.")

    if not isinstance(profile_instance, Profile):
        raise ValueError("profile_instance должен быть объектом Profile.")

    if permission_type == 'R':
        return

    if current_profile != profile_instance:
        raise PermissionDenied("У вас нет прав для выполнения этой операции с профилем.")

    # Если проверка прошла, доступ разрешен
    return