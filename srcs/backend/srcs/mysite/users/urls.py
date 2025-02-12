from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.UserViewSet, basename='user-list')
router.register(r'\w+', views.UserViewSet, basename='user-detail')

urlpatterns = [
    path('me/', views.UserAuthView.as_view()),
    path('', include(router.urls)),
]
