"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
# from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
	os.getenv('DOMAIN_NAME'),
]

# Application definition

# 추가된 앱들
INSTALLED_APPS = [
    'users',
    'oauth',
    'chat',
    'game_records',
    'follows',
    'daphne',
    'online_status',
]

INSTALLED_APPS += [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL 엔진 사용
        'NAME': os.getenv('POSTGRES_DB'),              # 데이터베이스 이름
        'USER': os.getenv('POSTGRES_USER'),              # 데이터베이스 사용자
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),               # 데이터베이스 비밀번호
        'HOST': os.getenv('POSTGRES_HOST'),                       # 데이터베이스 호스트 (localhost)
        'PORT': os.getenv('POSTGRES_PORT'),                            # PostgreSQL 기본 포트
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py
SESSION_ENGINE = "django.contrib.sessions.backends.db"  # DB 기반 세션 저장

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {  # 콘솔에 로그 출력
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {  # 파일에 로그 저장
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 'django': {  # Django 기본 로거
        #     'handlers': ['console', 'file'],
        #     'level': 'DEBUG',
        #     'propagate': True,
        # },
        'oauth': {  # 앱별 커스텀 로거
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'users': {  # 앱별 커스텀 로거
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'utils': {  # 앱별 커스텀 로거
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'chat': {  # 앱별 커스텀 로거
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
]

# REST Framework에 SimpleJWT를 기본 인증으로 설정
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'utils.permissions.IsTwoFactorAuthenticated',
    ),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # 액세스 토큰 유효 기간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # 리프레시 토큰 유효 기간
    # 'ACCESS_TOKEN_LIFETIME': timedelta(seconds=10),  # 액세스 토큰 유효 기간
    # 'REFRESH_TOKEN_LIFETIME': timedelta(minutes=1),    # 리프레시 토큰 유효 기간
    'ROTATE_REFRESH_TOKENS': True,                 # 리프레시 토큰 갱신 여부
    'BLACKLIST_AFTER_ROTATION': True,              # 갱신 후 이전 리프레시 토큰 블랙리스트 처리
    "SIGNING_KEY": os.getenv('SIGNING_KEY'), # tajeongtajeongtajeong
}

AUTH_USER_MODEL = 'users.CustomUser'

CSRF_TRUSTED_ORIGINS = ['https://localhost','https://*.127.0.0.1', 'https://10.16.220.226']

# asgi 설정
ASGI_APPLICATION = "config.asgi.application"

# 채널 레이어 설정
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("redis", 6379)],
#         },
#     },
# }
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 사용자 업로드 파일들이 저장될 디렉터리 경로 지정
MEDIA_ROOT = os.path.join(BASE_DIR, 'images')

# 브라우저에서 미디어 파일을 접근할 때 사용할 URL prefix
MEDIA_URL = '/images/'