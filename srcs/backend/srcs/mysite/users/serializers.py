# serializers.py
from rest_framework import serializers
from .models import CustomUser
import re, os

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_image', 'is_online']  # 필요한 필드만 선택
        read_only_fields = ['is_online']

    def validate(self, data):
        instance = self.instance
        for field, value in data.items():
            if getattr(instance, field) == value:
                raise serializers.ValidationError(f'The following field has not been changed: {field}')
        return super().validate(data)

    def update(self, instance, validated_data):
        if 'profile_image' in validated_data and instance.profile_image and os.path.isfile(instance.profile_image.path):
                os.remove(instance.profile_image.path)
        return super().update(instance, validated_data)

class CustomUserPatternSerializer(serializers.ModelSerializer):
    user_list = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['user_list']

    def get_user_list(self, partial_name):
        pattern = '^' + re.escape(partial_name)
        users_with_pattern = CustomUser.objects.filter(username__regex=pattern)
        return [user.username for user in users_with_pattern]
