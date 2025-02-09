# serializers.py
from rest_framework import serializers
from .models import OneOnOneMatch

class OneOnOneMatchSerializer(serializers.ModelSerializer):
    enemy = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = OneOnOneMatch
        fields = ['date', 'match_type', 'enemy', 'score', 'result']

    def get_enemy(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        return obj.get_enemy(request.user).username

    def get_score(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        return obj.get_score(request.user)

    def get_result(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        return obj.get_result(request.user)
