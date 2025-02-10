from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OneOnOneMatch
from users.models import CustomUser
from .serializers import MatchHistorySerializer
from django.db.models import Q

# Create your views here.
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
            return Response({"error": "No data"}, status=400)
        return Response(serializer.data)
#{
#    "total_match_history": [
#	      {
#		        "match_type": "배틀",
#		        "total_match": 100,
#		        "win": 50,
#		        "lose": 50,
#	      }
#	      {
#		        "match_type": "토너먼트",
#		        "total_match": 100,
#		        "win": 50,
#		        "lose": 50,
#	      }
#    ],
#    "match_history": [
#		    {
#		  	    "date": [2025, 2, 7],
#		        "match_type": "배틀",
#				    "enemy": "seojilee",
#				    "score": [4, 2], // my score가 배열의 시작
#				    "result": "win",
#		    },
#		    {
#			      "date": [2025, 2, 9],
#				    "match_type": "토너먼트",
#				    "enemy": {
#					    "player1": "seojilee",
#					    "player2": "taejeong",
#					    "player3": "hyoengsh",
#					    "player4": "junhapar",
#				    }
#				    "result": "lose", // win or lose
#		    },
#    ],
#}
