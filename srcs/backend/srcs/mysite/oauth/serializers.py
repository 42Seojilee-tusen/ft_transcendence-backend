# serializers.py
from rest_framework import serializers
from .models import TwoFactor

class TwoFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactor
        fields = ['two_factor_qr_code_image']  # 필요한 필드만 선택