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
        return Response(serializer.data)

class MatchViewSet(viewsets.ViewSet):
    #/api/games/[username]/
    def retrieve(self, request, pk=None):
        try:
            user = CustomUser.objects.get(username=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=400)
        serializer = MatchHistorySerializer(user)
        return Response(serializer.data)
