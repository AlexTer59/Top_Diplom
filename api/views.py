from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import *
from user.models import *
from .serializers import BoardSerializer, ListSerializer, TaskSerializer, TaskCommentSerializer
from .utils import *


# ==================== My Board =====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owned_boards(request):
    """Получение созданных пользователем досок"""
    profile = request.user.profile
    boards = Board.objects.filter(owner=profile)
    serializer = BoardSerializer(boards, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shared_boards(request):
    """Получение досок, в которые был приглашен"""
    profile = request.user.profile
    boards = Board.objects.filter(members=profile)
    serializer = BoardSerializer(boards, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detail_board(request, board_id):
    """Получение доски по ID"""

    try:
        board_instance = get_object_or_404(Board, id=board_id)
        check_board_access(request.user.profile, board_instance, 'R')
        serializer = BoardSerializer(board_instance)
        return Response(serializer.data)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== CRUD Board =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_board(request):
    """Создание новой доски"""
    try:
        profile = request.user.profile
        data = request.data.copy()
        data['owner'] = profile.id  # Передаем только ID профиля
        serializer = BoardSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_board(request, board_id):
    """Обновление списка по ID"""
    try:
        board_instance = get_object_or_404(Board, id=board_id)
        check_board_access(request.user.profile, board_instance, 'U')
        serializer = BoardSerializer(board_instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_board(request, board_id):
    """Удаление списка по ID"""
    try:
        board_instance = get_object_or_404(Board, id=board_id)
        check_board_access(request.user.profile, board_instance, 'D')
        board_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lists_by_board(request, board_id):
    """Получение всех списков для указанной доски по board_id"""
    try:
        board_instance = get_object_or_404(Board, id=board_id)
        check_list_access(request.user.profile, board_instance, 'R')
        lists = List.objects.filter(board_id=board_instance.id)
        serializer = ListSerializer(lists, many=True)
        return Response(serializer.data)
    except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_list(request, board_id):
    try:
        board_instance = get_object_or_404(Board, id=board_id)
        check_list_access(request.user.profile, board_instance, 'C')
        data = request.data.copy()
        data['board'] = board_instance.id  # Передаем только ID доски

        serializer = ListSerializer(data=data)

        if serializer.is_valid():
            serializer.save(board=board_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_list(request, board_id, list_id):
    """Обновление списка по ID"""
    try:
        list_instance = get_object_or_404(List, id=list_id)
        check_list_access(request.user.profile, list_instance, 'U')


        if list_instance.name.lower() == 'архив':
            raise ValidationError("Невозможно редактировать список 'Архив'.")

        serializer = ListSerializer(list_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_list(request, board_id, list_id):
    """Удаление списка по ID"""
    try:
        list_instance = get_object_or_404(List, id=list_id)
        check_list_access(request.user.profile, list_instance, 'D')

        # Проверка, если это столбец "Archive"
        if list_instance.name == "Архив":
            return Response({"error": "Столбец 'Архив' нельзя удалить."}, status=status.HTTP_400_BAD_REQUEST)

        list_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# ==================== My Task =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks_by_list(request, list_id):
    try:
        # Получаем доску по ID. Если не находим, возвращаем ошибку 404
        list_instance = get_object_or_404(List, id=list_id)

        # Проверяем есть ли у пользователя доступ
        check_task_access(request.user.profile, list_instance, 'R')

        # Получаем все задачи для указанного списка
        tasks = Task.objects.filter(status_id=list_instance.id)

        # Если списки найдены, сериализуем и возвращаем
        if tasks.exists():
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        else:
            # Если списки не найдены
            return Response({'message': 'No tasks found for this list.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================== CRUD Task =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request, board_id, list_id):
    try:
        """Создание новой задачи"""
        list_instance = get_object_or_404(List, id=list_id)
        board_instance = get_object_or_404(Board, id=board_id)
        check_task_access(request.user.profile, list_instance, 'C')

        data = request.data.copy()
        data['board'] = board_instance.id
        data['list'] = list_instance.id

        serializer = TaskSerializer(data=data, context={'request': request})


        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task(request, board_id, list_id, task_id):
    try:
        """Получение задачи"""
        task_instance = get_object_or_404(Task, id=task_id)
        check_task_access(request.user.profile, task_instance, 'R')

        serializer = TaskSerializer(task_instance)
        return Response(serializer.data)

    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_task(request, board_id, list_id, task_id):
    """Обновление задачи по ID"""
    try:
        task_instance = get_object_or_404(Task, id=task_id)
        check_task_access(request.user.profile, task_instance, 'U')
        serializer = TaskSerializer(task_instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
    # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, board_id, list_id, task_id):
    """Удаление списка по ID"""
    try:
        task_instance = get_object_or_404(Task, id=task_id)
        check_task_access(request.user.profile, task_instance, 'D')
        task_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
    # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_comments(request, task_id):
    """Получение заметок по задаче"""
    try:
        comments = TaskComment.objects.filter(task__id=task_id)
        task_instance = get_object_or_404(Task, id=task_id)
        check_task_access(request.user.profile, task_instance, 'R')
        serializer = TaskCommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, task_id):
    try:
        task_instance = get_object_or_404(Task, id=task_id)
        check_task_access(request.user.profile, task_instance, 'R')
        serializer = TaskCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_rest(request, task_id, comment_id):
    try:
        comment = get_object_or_404(TaskComment, id=comment_id)
        task = get_object_or_404(Task, id=task_id)
        profile = request.user.profile
        check_task_access(profile, task, 'R')

        like, created = TaskCommentLike.objects.get_or_create(comment=comment, profile=profile)

        if not created:
            like.delete()

        return Response(data={'is_liked': created}, status=status.HTTP_200_OK)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)