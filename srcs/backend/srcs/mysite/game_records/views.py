from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OneOnOneMatch
from users.models import CustomUser
from .serializers import MatchHistorySerializer

# Create your views here.
class MatchAuthView(APIView):
    def get(self, request):
        user = request.user
        serializer = MatchHistorySerializer(user)
        if not serializer.data.get('match_history'):
            return Response({"error": "Data not found"}, status=400)
        return Response(serializer.data)

class MatchView(APIView):
    def get(self, request, username=None):
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=400)
        serializer = MatchHistorySerializer(user)
        if not serializer.data.get('match_history'):
            return Response({"error": "Data not found"}, status=400)
        return Response(serializer.data)
