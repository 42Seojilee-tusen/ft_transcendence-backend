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
from users.models import CustomUser, Follows
from .serializers import CustomUserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
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

class UserFollowView(APIView):
    def get(self, request):
        user = request.user
        
        follows = Follows.objects.filter(user=user)
        
        friend_list = []
        for follow in follows:
            friend_list.append(follow.follow_user.username)
        
        return Response({
            'friend_list': friend_list
        })
    
    def post(self, request):
        check_json_data(request, ['username'])
        username = request.data.get('username')
        
        try:
            follow_user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        
        if user == follow_user:
            return Response({'error': 'Same user'}, status=404)

        # 이미 친구로 추가된 상태인지 확인
        if Follows.objects.filter(user=user, follow_user=follow_user).exists():
            return Response({"error": "Already friends"}, status=status.HTTP_400_BAD_REQUEST)

        # 친구 관계 생성
        Follows.objects.create(user=user, follow_user=follow_user)
        return Response({"message": f"{follow_user.username} has been added as a friend."}, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        check_json_data(request, ['username'])
        username = request.data.get('username')
        user = request.user
        
        try:
            follow_user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            delete_follow_user = Follows.objects.get(user=user, follow_user=follow_user)
        except Follows.DoesNotExist:
            return Response({"error": "not follow"}, status=status.HTTP_404_NOT_FOUND)

        # 친구 관계 생성
        delete_follow_user.delete()
        # Follows.objects.delete(user=user, follow_user=follow_user)
        return Response({"message": f"{follow_user.username} has been deleted as a friend."}, status=status.HTTP_201_CREATED)
        