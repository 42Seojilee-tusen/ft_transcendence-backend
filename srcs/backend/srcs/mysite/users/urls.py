from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserView.as_view()),
    path('auth', views.UserAuthView.as_view()),
    # path('auth/login', views.login),
    # path('auth/callback', views.login_callback),
]