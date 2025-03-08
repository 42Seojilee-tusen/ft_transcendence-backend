from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from . import views

urlpatterns = [
    path('me/', views.MatchAuthView.as_view()),
    path('<str:username>/', views.MatchView.as_view()),
]
