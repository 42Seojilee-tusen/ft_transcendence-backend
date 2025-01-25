from django.http import JsonResponse

def get_access_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', None)
    if not token:
        return JsonResponse({
            'error': 'Authorization 헤더가 없습니다.'
        }, status=400)

    # Bearer 토큰 분리
    if token.startswith("Bearer "):
        access_token = token.split("Bearer ")[1]
    else:
        return JsonResponse({
            'error': '유효한 Bearer 토큰이 아닙니다.'
        }, status=400)
    return access_token