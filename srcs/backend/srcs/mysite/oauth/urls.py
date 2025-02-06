from django.urls import path
from . import views
# from rest_framework_simplejwt.views import (
#     TokenRefreshView,
# )

urlpatterns = [
    # # csrf토큰 발급용 api
    path('csrf', views.CsrfTokenView.as_view()),
    
    # # jwt token관련 api
    path('token', views.TokenView.as_view()),
    path('token/refresh', views.TokenRefreshView.as_view()),

    # # 2fa 관련 api
    path('2fa', views.TwoFactorView.as_view()),
]