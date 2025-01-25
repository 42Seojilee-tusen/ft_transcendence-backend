from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('auth/login', views.login),
    path('auth/callback', views.login_callback),
]