import requests
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken

import os
from dotenv import load_dotenv
from utils.validation import validate_data, validate_header
from django.views.decorators.csrf import csrf_protect
from users.models import TCDUser
import json

import logging
logger = logging.getLogger('oauth') 
# Create your views here.

# csrf 토큰을 받기위한 GET 메서드
@csrf_protect
def crsf(request):
    if request.method == 'GET':
        return HttpResponse("crsf_get")
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
                "first_name": api_response["first_name"],
                "last_name": api_response["last_name"],
                "image_url": api_response["image"]["link"],
            },
        )

        refresh_token = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh_token':str(refresh_token),
            'access_token':str(refresh_token.access_token)
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

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