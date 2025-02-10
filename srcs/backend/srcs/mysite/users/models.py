from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    id = models.IntegerField(primary_key=True, blank=True,help_text="유저 고유 id")
    email = models.CharField(max_length=100, blank=True, help_text="인트라 이메일")
    profile_image = models.FileField(upload_to='profiles/', null=True, help_text="프로필 이미지 경로")
