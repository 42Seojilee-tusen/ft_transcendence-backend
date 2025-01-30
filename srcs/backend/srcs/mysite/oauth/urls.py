from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # csrf토큰 발급용 api
    path('csrf', views.crsf),
    
    # jwt token관련 api
    path('token', views.token),
    path('token/refresh', TokenRefreshView.as_view()),

    # 2fa 관련 api
    path('2fa', views.qrcode_image),
    path('2fa/refresh', views.refresh_qrcode_image),

    # 테스트 api
    path('2fa/image', views.show_qr_image),
    path('2fa/authorize', views.authorisation_2fa),
    path('callback', views.callback),
    path('login', views.login),
]