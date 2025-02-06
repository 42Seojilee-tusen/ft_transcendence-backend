from django.db import models
from users.models import CustomUser
# Create your models here.

class TwoFactor(models.Model):
    custom_user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE, help_text="유저 외래키")
    two_factor_qr_code_image = models.FileField(upload_to='two_factor_qr_code/', null=True, help_text="2FA 등록 QR코드 이미지 경로")
    two_factor_secret_code = models.CharField(max_length=100, null=True, help_text="2FA 고유 시크릿 키")