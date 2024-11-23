from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

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