from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from .utils import *
from api.utils import *
from user.models import Profile
from user.serializers import ProfileSerializer, SubscriptionSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profiles(request):
    """Получение пользователей за исключением авторизованного"""
    profiles = Profile.objects.exclude(id=request.user.profile.id)
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription(request):
    """Получение данных о подписке авторизованного пользователя"""
    try:
        profile = request.user.profile
        check_subscription_access(request.user.profile, profile, 'R')
        subscription = get_object_or_404(Subscription, profile=profile)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profiles_by_board(request, board_id):
    """Получение информации о пользователях участвующих в доске и создателе"""
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
    """Получение информации о пользователе"""
    try:
        profile = get_object_or_404(Profile, id=profile_id)
        check_profile_access(request.user.profile, profile, 'R')
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    except PermissionDenied as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        # Обработка других ошибок
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_profile(request, profile_id):
    """Получение информации о пользователе"""
    try:
        profile = get_object_or_404(Profile, id=profile_id)
        check_profile_access(request.user.profile, profile, 'U')
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
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


