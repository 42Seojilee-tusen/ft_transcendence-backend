# serializers.py
from rest_framework import serializers
from .models import TCDUser

class TCDUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCDUser
        fields = ['id', 'login', 'first_name', 'last_name', 'image_url']  # 필요한 필드만 선택