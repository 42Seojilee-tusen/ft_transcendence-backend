from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/oauth/', include('oauth.urls')),
    path('api/users/', include('users.urls')),
    path('chat/', include('chat.urls')),
    re_path(r'^api/images/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

