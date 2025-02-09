# serializers.py
from rest_framework import serializers
from .models OneOnOneMatch

class OneOnOneMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = OneOnOneMatch
        fields = ['date', 'match_type', 'enemy', 'score', 'result']
