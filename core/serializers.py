from rest_framework import serializers
from .models import Board, List, Task
from user.models import Profile
from user.serializers import ProfileSerializer

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'description', 'owner', 'members']

class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'name', 'board', 'position']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = ProfileSerializer()           # Поле assigned_to будет сериализовано как Profile

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'board', 'list', 'position', 'due_date', 'created_at', 'updated_at', 'labels', 'assigned_to']