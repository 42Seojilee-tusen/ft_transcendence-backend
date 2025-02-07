from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError
from utils.validation import check_json_data
from users.models import CustomUser
from .serializers import CustomUserSerializer
import logging
logger = logging.getLogger('users') 

# Create your views here.

class UserAuthViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['get'], url_path='')
    def get_auth_user(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # override the basic retrieve() to search user by username, not by primary key
    def retrieve(self, request, pk=None):
        user = get_object_or_404(CustomUser, username=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
