from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from utils.validation import check_json_data
from users.models import CustomUser
from .serializers import CustomUserSerializer, CustomUserPatternSerializer
import logging
logger = logging.getLogger('users') 

# Create your views here.

class UserAuthView(APIView):
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        data = request.data
        if not data:
            return Response({'error': 'The request body is empty.'}, status=400)
        serializer = CustomUserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'error': 'Cannot update user'}, status=400)


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # /api/users/find?partial_name=[name]
    @action(detail=False, methods=['get'], url_path='find')
    def find_user_by_pattern(self, request):
        partial_name = request.GET.get('partial_name')
        serializer = CustomUserPatternSerializer(partial_name)
        if not serializer.data.get('user_list'):
            return Response({'error': 'User not found'}, status=400)
        return Response(serializer.data)

    # override the basic retrieve() to search user by username, not by primary key
    def retrieve(self, request, pk=None):
        try:
            user = CustomUser.objects.get(username=pk)
            serializer = CustomUserSerializer(user)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
        return Response(serializer.data)
