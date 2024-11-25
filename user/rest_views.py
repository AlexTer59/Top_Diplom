from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from .utils import *
from api.utils import *
from user.models import Profile
from user.serializers import ProfileSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profiles(request):
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profiles_by_board(request, board_id):
    try:
        board_instance = get_object_or_404(Board, id=board_id)
        members = board_instance.members.all()
        owner = board_instance.owner
        profiles = [owner] + list(members)
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок

        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_detail(request, profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['POST'])
def create_profile(request):
    print(request.data)
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)