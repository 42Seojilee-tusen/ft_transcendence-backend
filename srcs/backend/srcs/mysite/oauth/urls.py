from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
urlpatterns = [
    path('csrf', views.crsf),
    path('token', views.token),
    path('callback', views.callback),
    path('login', views.login),
    path('refresh', TokenRefreshView.as_view()),
]