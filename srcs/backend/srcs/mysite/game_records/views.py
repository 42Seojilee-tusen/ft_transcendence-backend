from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OneOnOneMatch
from users.models import CustomUser
from .serializers import MatchHistorySerializer

# Create your views here.
class MatchAuthViewSet(viewsets.ViewSet):
    #/api/games/me/
    def list(self, request):
        user = request.user
        serializer = MatchHistorySerializer(user)
        if not serializer.data.get('match_history'):
            return Response({"error": "Data not found"}, status=400)
        return Response(serializer.data)

class MatchViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = []

    #/api/games/[username]/
    def retrieve(self, request, pk=None):
        try:
            user = CustomUser.objects.get(username=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=400)
        serializer = MatchHistorySerializer(user)
        if not serializer.data.get('match_history'):
            return Response({"error": "Data not found"}, status=400)
        return Response(serializer.data)
