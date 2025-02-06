# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed

# class TwoFactorJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         user_token_tuple = super().authenticate(request)  # 기본 JWT 인증 수행
#         if user_token_tuple is None:
#             return None

#         user, token = user_token_tuple
#         if not token.get('is_2fa_authenticated', False):
#             raise AuthenticationFailed("2FA 인증이 필요합니다.")

#         return user, token  # 2FA 인증된 사용자 반환
from rest_framework.permissions import BasePermission

class IsTwoFactorAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.auth and request.auth.get('is_2fa_authenticated', False)
