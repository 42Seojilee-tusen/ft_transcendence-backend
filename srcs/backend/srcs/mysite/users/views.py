from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from users.models import TCDUser
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError
from utils.validation import validate_data
from utils.authentication import get_access_token
from .serializers import TCDUserSerializer
import logging
logger = logging.getLogger('users') 

# Create your views here.
class UserView(APIView):
    def get(self, request):
        users = TCDUser.objects.all()  # QuerySet 가져오기
        serializer = TCDUserSerializer(users, many=True)  # many=True 옵션
        return JsonResponse(serializer.data, safe=False)


class UserAuthView(APIView):
    def get(self, request):
        access_token = get_access_token(request)
        try:
            # Access Token 검증
            token = AccessToken(access_token)  # 토큰 서명 및 유효성 검증
        except TokenError as e:
            # 검증 실패 (만료되었거나, 위조된 토큰)
            return JsonResponse({'message': f'Token is invalid: {str(e)}'}, status=401)
        # 검증 성공 시, 토큰의 페이로드 확인 가능
        user_id = token['user_id']  # 페이로드에서 user_id 추출

        # TCDUser 모델에서 user_id에 해당하는 사용자 정보 가져오기
        # user = get_object_or_404(TCDUser, id=user_id)
        user = TCDUser.objects.get(id = user_id)
        
        serializer = TCDUserSerializer(user)

        return JsonResponse({
            "message": "Token is valid",
            "user": serializer.data
        })