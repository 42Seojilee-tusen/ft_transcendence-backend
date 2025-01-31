import requests
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

import os
from dotenv import load_dotenv
from utils.validation import validate_data, validate_header
from utils.authentication import get_access_token
from django.views.decorators.csrf import csrf_protect
from users.models import TCDUser
import json
import pyotp
import qrcode

import logging
logger = logging.getLogger('oauth') 
# Create your views here.

# csrf 토큰을 받기위한 GET 메서드
@csrf_protect
def crsf(request):
    if request.method == 'GET':
        return JsonResponse({'message':"crsf_get"}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# jwt토큰 반환 API
def token(request):
    if request.method == 'POST':
        error_response = validate_data(request, ['code'])
        if error_response:
            return error_response

        body_data = json.loads(request.body)
        code = body_data.get('code')

        token_url = "https://api.intra.42.fr/oauth/token"
        data = {
            "code": code,
            "client_id": os.getenv("UID_KEY"),
            "client_secret": os.getenv("SECRET_KEY"),
            "redirect_uri": os.getenv("REDIRECTION_URI"),
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=data).json()
        if "error" in token_response:
            return JsonResponse({"error": token_response["error"]}, status=400)

        api_url = "https://api.intra.42.fr/v2/me"
        headers = {"Authorization": f"Bearer {token_response["access_token"]}"}
        api_response = requests.get(api_url, headers=headers).json()

        user, created = TCDUser.objects.update_or_create(
            id = api_response["id"],
            defaults = {
                "login": api_response["login"],
                "email": api_response["email"],
                "first_name": api_response["first_name"],
                "last_name": api_response["last_name"],
                "image_url": api_response["image"]["link"],
            },
        )

        two_factor_secret_key = user.two_factor_secret_key

        refresh_token = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token),
            'two_factor_required': not bool(two_factor_secret_key)
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def qrcode_image(request):
    if request.method == 'GET':
        access_token = get_access_token(request)
        try:
            # Access Token 검증
            token = AccessToken(access_token)  # 토큰 서명 및 유효성 검증
        except TokenError as e:
            # 검증 실패 (만료되었거나, 위조된 토큰)
            return JsonResponse({'message': f'Token is invalid: {str(e)}'}, status=401)
        user_id = token['user_id']  # 페이로드에서 user_id 추출

        # TCDUser 모델에서 user_id에 해당하는 사용자 정보 가져오기
        user = TCDUser.objects.get(id = user_id)

        # user에게 등록된 2fa코드가 이미 있다면 에러 반환
        if bool(user.two_factor_secret_key):
            return JsonResponse({
                'error':'이미 등록된 유저입니다.'
            }, status=401)
        
        # qrcode url생성하는데 필요한 변수들
        issuer = os.getenv('DJANGO_ISSUER')
        account_name = user.email
        secret = pyotp.random_base32()
        
        # 2fa 비밀키를 데이터베이스에 저장
        # [fix point] 추후 암호화해서 저장하는 로직이 필요함.
        user.two_factor_secret_key = secret
        user.save()
        
        qrCodeUrl = f"otpauth://totp/{issuer}:{account_name}?secret={secret}&issuer={issuer}"
        # qr = qrcode.make(qrCodeUrl)
        # qr.save(f"images/{user.login}_2fa_qr_code.png")  # 파일로 저장
        # file_path = f"./images/{user.login}_2fa_qr_code.png"

        # return FileResponse(open(file_path, "rb"), content_type="image/png")
        return JsonResponse({
            'qrCodeUrl':qrCodeUrl
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def refresh_qrcode_image(request):
    if request.method == 'GET':
        access_token = get_access_token(request)
        try:
            # Access Token 검증
            token = AccessToken(access_token)  # 토큰 서명 및 유효성 검증
        except TokenError as e:
            # 검증 실패 (만료되었거나, 위조된 토큰)
            return JsonResponse({'message': f'Token is invalid: {str(e)}'}, status=401)
        user_id = token['user_id']  # 페이로드에서 user_id 추출

        # TCDUser 모델에서 user_id에 해당하는 사용자 정보 가져오기
        user = TCDUser.objects.get(id = user_id)

        # 등록되지 않았아면 리프레시 해주지 않음.
        if not bool(user.two_factor_secret_key):
            return JsonResponse({
                'error':'아직 등록되지 않았습니다.'
            }, status=401)
        issuer = os.getenv('DJANGO_ISSUER')
        account_name = user.email
        secret = pyotp.random_base32()
        
        user.two_factor_secret_key = secret
        user.save()
        
        qrCodeUrl = f"otpauth://totp/{issuer}:{account_name}?secret={secret}&issuer={issuer}"
        # qr = qrcode.make(qrCodeUrl)
        # qr.save(f"images/{user.login}_2fa_qr_code.png")  # 파일로 저장
        # file_path = f"./images/{user.login}_2fa_qr_code.png"

        # return FileResponse(open(file_path, "rb"), content_type="image/png")
        return JsonResponse({
            'qrCodeUrl':qrCodeUrl
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# 2fa 검증용 코드
def authorisation_2fa(request):
    user_otp = request.GET.get('user_otp')
    access_token = get_access_token(request)
    try:
        token = AccessToken(access_token)
    except TokenError as e:
        return JsonResponse({'message': f'Token is invalid: {str(e)}'}, status=401)
    user_id = token['user_id']
    
    user = TCDUser.objects.get(id = user_id)
    totp = pyotp.TOTP(user.two_factor_secret_key)
    otp = totp.now()
    if otp == user_otp:
        return JsonResponse({
            'message': '코드가 올바릅니다',
            'correct_otp': otp,
            'user_otp': user_otp
        }, status=200)
    return JsonResponse({
        'error': '코드가 다릅니다.',
        'correct_otp': otp,
        'user_otp': user_otp
    }, status=401)

# FE가 해줘야하는 로직
def show_qr_image(request):
    qrCodeUrl = request.GET.get('qrCodeUrl')
    qr = qrcode.make(qrCodeUrl)
    qr.save(f"images/2fa_qr_code.png")  # 파일로 저장
    file_path = f"./images/2fa_qr_code.png"
    return FileResponse(open(file_path, "rb"), content_type="image/png")

# FE가 해줘야하는 로직
def callback(request):
    code = request.GET.get('code')
    return JsonResponse({"code": code})

# FE가 해줘야하는 로직
def login(request):
    auth_url = os.getenv("AUTH_URL")
    client_id = os.getenv("UID_KEY")
    redirect_uri = os.getenv("REDIRECTION_URI")
    response_type = "code"

    auth_url = f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}"
    return redirect(auth_url)