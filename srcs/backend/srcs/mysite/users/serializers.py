# serializers.py
from rest_framework import serializers
from .models import CustomUser
import re

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_image']  # 필요한 필드만 선택

class CustomUserPatternSerializer(serializers.ModelSerializer):
    user_list = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['user_list']

    def get_user_list(self, partial_name):
        pattern = '^' + re.escape(partial_name)
        users_with_pattern = CustomUser.objects.filter(username__regex=pattern)
        return [user.username for user in users_with_pattern]
