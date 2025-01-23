import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from api.models import TCDUser
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import logging

logger = logging.getLogger('api') 
# Create your views here.

def index(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return HttpResponse("아직 로그인되어있지 않습니다.")

    access_token = auth_header.split(' ')[1]  # "Bearer <token>"에서 <token>만 추출
    try:
        # Access Token 검증
        token = AccessToken(access_token)  # 토큰 서명 및 유효성 검증

        # 검증 성공 시, 토큰의 페이로드 확인 가능
        user_id = token['user_id']  # 페이로드에서 user_id 추출

        # TCDUser 모델에서 user_id에 해당하는 사용자 정보 가져오기
        user = get_object_or_404(TCDUser, id=user_id)

        return JsonResponse({
            "message": "Token is valid",
            "user": {
                "id": user.id,
                "login": user.login,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "image_url": user.image_url,
            }
        })

    except TokenError as e:
        # 검증 실패 (만료되었거나, 위조된 토큰)
        return JsonResponse({'message': f'Token is invalid: {str(e)}'}, status=401)

# 로그인 페이지
def login(request):
    auth_url = "https://api.intra.42.fr/oauth/authorize"
    client_id = "u-s4t2ud-c380f46281110b1a4bacedf94922414a41c33a04f9ea0718674e7ea66232fb26"
    redirect_uri = "http://localhost:8000/api/auth/callback"
    response_type = "code"

    auth_url = f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}"
    return redirect(auth_url)

# 로그인 후 돌아올 페이지
# 이후 우리가 원하는 페이지로 이동
def login_callback(request):
    code = request.GET.get("code")  # Authorization Code
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    # Token 요청
    token_url = "https://api.intra.42.fr/oauth/token"

    data = {
        "code": code,
        "client_id": "u-s4t2ud-c380f46281110b1a4bacedf94922414a41c33a04f9ea0718674e7ea66232fb26",
        "client_secret": "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",
        "redirect_uri": "http://localhost:8000/api/auth/callback",
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    token_response = response.json()

    if "error" in token_response:
        return JsonResponse({"error": token_response["error"]}, status=400)
    
    access_token = token_response["access_token"]
    expires_in = token_response["expires_in"]
    refresh_token = token_response["refresh_token"]

    api_url = "https://api.intra.42.fr/v2/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(api_url, headers=headers).json()

    user, created = TCDUser.objects.update_or_create(
        id = response["id"],
        defaults = {
            "login": response["login"],
            "first_name": response["first_name"],
            "last_name": response["last_name"],
            "image_url": response["image"]["link"],
        },
    )
    
    if created:
        logging.info(f"새로운 유저가 생성되었습니다: {user}")
    else:
        logging.info(f"기존 유저가 업데이트되었습니다: {user}")
    refresh = RefreshToken.for_user(user)
    
    response = JsonResponse({
        "message": "Login successful",
        "access_token": str(refresh.access_token),
    })

    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=True,
        samesite='Lax',
    )

    return response
