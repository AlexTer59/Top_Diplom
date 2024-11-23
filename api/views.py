from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import Board, List, Task
from .serializers import BoardSerializer, ListSerializer, TaskSerializer


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
    """Получение досоки по ID"""
    profile = request.user.profile
    try:
        board_instance = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)
    if board_instance.owner != profile and not board_instance.members.filter(id=profile.id).exists():
        return Response({'error': 'You do not have permission to view this board.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = BoardSerializer(board_instance)
    return Response(serializer.data)


# ==================== CRUD Board =====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_board(request):
    """Создание новой доски"""
    serializer = BoardSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_board(request, board_id):
    """Обновление списка по ID"""
    try:
        board_instance = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BoardSerializer(board_instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_board(request, board_id):
    """Удаление списка по ID"""
    profile = request.user.profile
    try:
        board_instance = Board.objects.get(id=board_id)
        if board_instance.owner == profile:
            board_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Only the owner can delete a board'}, status=status.HTTP_403_FORBIDDEN)
    except Board.DoesNotExist:
        return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)



# ==================== My List =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lists_by_board(request, board_id):
    """Получение всех списков для указанной доски по board_id"""
    profile = request.user.profile

    # Получаем доску по ID. Если не находим, возвращаем ошибку 404
    board = get_object_or_404(Board, id=board_id)

    # Проверяем, является ли пользователь владельцем или участником доски
    if board.owner != profile and profile not in board.members.all():
        return Response({'error': 'You do not have permission to view this board.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Фильтруем списки по board_id
        lists = List.objects.filter(board_id=board_id)

        # Если списки найдены, сериализуем и возвращаем
        if lists.exists():
            serializer = ListSerializer(lists, many=True)
            return Response(serializer.data)
        else:
            # Если списки не найдены
            return Response({'message': 'No lists found for this board.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================== CRUD List =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_lists(request):
    """Получение всех списков"""
    lists = List.objects.all()
    serializer = ListSerializer(lists, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_list(request):
    """Создание нового списка"""
    serializer = ListSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_list(request, list_id):
    """Обновление списка по ID"""
    try:
        list_instance = List.objects.get(id=list_id)
    except List.DoesNotExist:
        return Response({'error': 'List not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ListSerializer(list_instance, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_list(request, list_id):
    """Удаление списка по ID"""
    try:
        list_instance = List.objects.get(id=list_id)
        list_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except List.DoesNotExist:
        return Response({'error': 'List not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== My Task =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks_by_list(request, list_id):
    profile = request.user.profile

    # Получаем доску по ID. Если не находим, возвращаем ошибку 404
    list_instance = get_object_or_404(List, id=list_id)

    # Получаем доску, к которой относится этот список
    board = list_instance.board

    # Проверяем, является ли пользователь владельцем или участником доски
    if board.owner != profile and profile not in board.members.all():
        return Response({'error': 'You do not have permission to view this board.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Получаем все задачи для указанного списка
        tasks = Task.objects.filter(list_id=list_id)

        # Если списки найдены, сериализуем и возвращаем
        if tasks.exists():
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        else:
            # Если списки не найдены
            return Response({'message': 'No tasks found for this list.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================== CRUD Task =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    """Получение всех задач"""
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """Создание новой задачи"""
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task(request, task_id):
    """Обновление задачи по ID"""
    try:
        task_instance = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task_instance, data=request.data, partial=True)
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
