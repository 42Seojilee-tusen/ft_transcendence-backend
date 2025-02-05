from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
class UserView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        users = CustomUser.objects.all()  # QuerySet 가져오기
        serializer = CustomUserSerializer(users, many=True)  # many=True 옵션
        return Response(serializer.data)


class UserAuthView(APIView):
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)