# serializers.py
from rest_framework import serializers
from .models import Follows
from users.serializers import CustomUserSerializer

class FollowsSerializer(serializers.ModelSerializer):
    follow_user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Follows
        fields = ['follow_user']  # 필요한 필드만 선택