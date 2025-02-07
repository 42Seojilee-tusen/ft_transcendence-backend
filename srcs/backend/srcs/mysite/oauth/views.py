import requests
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from utils.decorators import require_http_methods
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

import os
from dotenv import load_dotenv
from utils.validation import check_json_data
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from .models import TwoFactor
from .serializers import TwoFactorSerializer
from users.models import CustomUser
from users.serializers import CustomUserSerializer
import json
import pyotp
import qrcode
from django.conf import settings

from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny
from django.core.files.storage import default_storage

import logging
logger = logging.getLogger('oauth') 

# Create your views here.

# csrf 토큰을 받기위한 GET 메서드

# @method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfTokenView(APIView):
    # @ensure_csrf_cookie
    def get(self, request):

        return Response({
            'message': 'csrf_get'
        })


class TokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        check_json_data(request, ['code'])
        code = request.data.get('code')

        token_url = "https://api.intra.42.fr/oauth/token"
        data = {
            "code": code,
            "client_id": os.getenv("UID_KEY"),
            "client_secret": os.getenv("SECRET_KEY"),
            "redirect_uri": os.getenv("REDIRECTION_URI"),
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=data)
        if token_response.status_code != 200:
            return Response(token_response.json(), status=token_response.status_code)
        token_data = token_response.json()

        api_url = "https://api.intra.42.fr/v2/me"
        headers = {"Authorization": f"Bearer {token_data["access_token"]}"}

        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code != 200:
            return Response(api_response.json(), status=api_response.status_code)
        api_data = api_response.json()

        user, created = CustomUser.objects.get_or_create(
            id = api_data['id'],
            username = api_data['login'],
            email = api_data['email'],
        )

        file_name = f'_{user.id}.png'
        file_path = user.profile_image.field.upload_to + '/' + file_name

        if not default_storage.exists(file_path):
            image_response = requests.get(api_data["image"]["link"])
            if image_response.status_code != 200:
                return Response(image_response.json(), status=image_response.status_code)
            user.profile_image.save(file_name, ContentFile(image_response.content), save=True)

        refresh_token = RefreshToken.for_user(user)
        refresh_token['is_2fa_authenticated'] = False
        access_token = refresh_token.access_token
        access_token['is_2fa_authenticated'] = False
        
        response = Response({
            'access_token': str(access_token),
        })

        response.set_cookie(
            key='refresh_token',
            value=str(refresh_token),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60
        )
        return response


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        old_refresh_token = request.COOKIES.get('refresh_token')
        try:
            old_refresh_token = RefreshToken(old_refresh_token)
        except TokenError as e:
            error_message = {
                "detail": "Given token not valid for any token type",
                "code": "token_not_valid",
                "messages": [
                    {
                        "token_class": "RefreshToken",
                        "token_type": "refresh",
                        "message": str(e)
                    }
                ]
            }
            return Response(error_message, status=401)
        user = CustomUser.objects.get(id=old_refresh_token['user_id'])

        new_refresh_token = RefreshToken.for_user(user)
        new_refresh_token['is_2fa_authenticated'] = old_refresh_token['is_2fa_authenticated']
        new_access_token = new_refresh_token.access_token
        new_access_token['is_2fa_authenticated'] = old_refresh_token['is_2fa_authenticated']

        response = Response({
            'access_token': str(new_access_token),
        })
        response.set_cookie(
            key='refresh_token',
            value=str(new_refresh_token),
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=7 * 24 * 60 * 60
        )
        return response

class TwoFactorView(APIView):
    permission_classes = []
    def get(self, request):
        user = request.user

        # qrcode url생성하는데 필요한 변수들
        issuer = os.getenv('DJANGO_ISSUER')
        account_name = user.email
        secret = pyotp.random_base32()

        qr_code_url = f"otpauth://totp/{issuer}:{account_name}?secret={secret}&issuer={issuer}"
        qr = qrcode.make(qr_code_url)

        # 이미지 저장 경로 설정
        file_name = f"_{user.id}_2fa_qr_code.png"
        relative_path = f"two_factor_qr_code/{file_name}"  # MEDIA_ROOT 하위 경로
        full_path = f"{settings.MEDIA_ROOT}/{relative_path}"
        qr.save(full_path)  # 파일로 저장

        # 2fa 비밀키를 데이터베이스에 저장
        # [fix point] 추후 암호화해서 저장하는 로직이 필요함.
        two_factor, created = TwoFactor.objects.get_or_create(custom_user=user)
        two_factor.two_factor_secret_code = secret
        two_factor.two_factor_qr_code_image.name = relative_path  # FileField에 상대 경로 저장
        two_factor.save()

        serializer = TwoFactorSerializer(two_factor, many=False)  # many=True 옵션
        return Response(serializer.data, status=200)

    def post(self, request):
        check_json_data(request, ['otp_code'])
        otp_code = request.data.get('otp_code')
        user = request.user

        totp = pyotp.TOTP(user.twofactor.two_factor_secret_code)
        cur_otp_code = totp.now()
        if cur_otp_code == otp_code:
            refresh_token = RefreshToken.for_user(user)
            refresh_token['is_2fa_authenticated'] = True
            access_token = refresh_token.access_token
            access_token['is_2fa_authenticated'] =True

            response = Response({
                'access_token': access_token
            })

            response.set_cookie(
                key='refresh_token',
                value=str(refresh_token),
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60
            )
            return response
        return Response({
            'error': '인증코드가 틀렸습니다.'
        }, status=403)