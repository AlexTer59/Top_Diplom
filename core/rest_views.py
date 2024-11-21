from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Board, List, Task
from .serializers import BoardSerializer, ListSerializer, TaskSerializer

# ==================== CRUD Board =====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_boards(request):
    """Получение всех досок"""
    boards = Board.objects.all()
    serializer = BoardSerializer(boards, many=True)
    return Response(serializer.data)

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
    try:
        board_instance = Board.objects.get(id=board_id)
        board_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Board.DoesNotExist:
        return Response({'error': 'Board not found'}, status=status.HTTP_404_NOT_FOUND)

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