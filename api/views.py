from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import *
from user.models import *
from .serializers import BoardSerializer, ListSerializer, TaskSerializer
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
    profile = request.user.profile
    data = request.data.copy()
    data['owner'] = profile.id  # Передаем только ID профиля
    serializer = BoardSerializer(data=data)
    if serializer.is_valid():
        serializer.save(owner=profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_board(request, board_id):
    """Обновление списка по ID"""
    try:
        board_instance = get_object_or_404(Board, id=board_id)
        check_board_access(request.user.profile, board_instance, 'U')
        serializer = BoardSerializer(board_instance, data=request.data, partial=True)
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
        tasks = Task.objects.filter(list_id=list_instance.id)

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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    """Обновление задачи по ID"""
    try:
        task_instance = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task_instance, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    """Удаление списка по ID"""
    try:
        task_instance = Task.objects.get(id=task_id)
        task_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


