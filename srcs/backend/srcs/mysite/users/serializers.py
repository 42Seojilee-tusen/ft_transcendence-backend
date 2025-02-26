# serializers.py
from rest_framework import serializers
from .models import CustomUser
import re

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_image']  # 필요한 필드만 선택

    def validate(self, data):
        instance = self.instance
        for field, value in data.items():
            if getattr(instance, field) == value:
                raise serializers.ValidationError(f'The following field has not been changed: {field}')
        return super().validate(data)

class CustomUserPatternSerializer(serializers.ModelSerializer):
    user_list = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['user_list']

    def get_user_list(self, partial_name):
        pattern = '^' + re.escape(partial_name)
        users_with_pattern = CustomUser.objects.filter(username__regex=pattern)
        return [user.username for user in users_with_pattern]
