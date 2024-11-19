from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Board, List, Task
from .serializers import BoardSerializer, ListSerializer, TaskSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем доски, доступные пользователю
        return self.request.user.profile.shared_boards.all() | self.request.user.profile.owned_boards.all()

class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем списки по доступным доскам
        user_boards = self.request.user.profile.shared_boards.all() | self.request.user.profile.owned_boards.all()
        return List.objects.filter(board__in=user_boards)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем задачи по доступным доскам
        user_boards = self.request.user.profile.shared_boards.all() | self.request.user.profile.owned_boards.all()
        return Task.objects.filter(board__in=user_boards)
