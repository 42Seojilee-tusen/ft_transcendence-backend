from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

FORBIDDEN_PATTERNS = { 'me', 'find', 'usernames' }

def validate_username(pattern):
    if pattern in FORBIDDEN_PATTERNS:
        raise ValidationError(f'Cannot use {pattern} as username')

def set_unique_filename(instance, filename):
    extension = filename.split('.')[-1]
    return f'profiles/_{instance.id}.{extension}'

class CustomUser(AbstractUser):
    id = models.IntegerField(primary_key=True, blank=True,help_text="유저 고유 id")
    email = models.CharField(max_length=100, blank=True, help_text="인트라 이메일")
    profile_image = models.FileField(upload_to=set_unique_filename, null=True, help_text="프로필 이미지 경로")
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validate_username]
    )
