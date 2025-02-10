from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.validation import check_json_data
from .models import Follows
from users.models import CustomUser
# Create your views here.

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
            return Response({"error": "User not found"}, status=400)
        user = request.user

        if user == follow_user:
            return Response({'error': 'Same user'}, status=400)

        # 이미 친구로 추가된 상태인지 확인
        if Follows.objects.filter(user=user, follow_user=follow_user).exists():
            return Response({"error": "Already friends"}, status=400)

        # 친구 관계 생성
        Follows.objects.create(user=user, follow_user=follow_user)
        return Response({"message": f"{follow_user.username} has been added as a friend."}, status=200)

    def delete(self, request):
        check_json_data(request, ['username'])
        username = request.data.get('username')
        user = request.user
        
        try:
            follow_user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=400)

        try:
            delete_follow_user = Follows.objects.get(user=user, follow_user=follow_user)
        except Follows.DoesNotExist:
            return Response({"error": "not follow"}, status=400)

        # 친구 관계 삭제
        delete_follow_user.delete()
        return Response({"message": f"{follow_user.username} has been deleted as a friend."}, status=200)