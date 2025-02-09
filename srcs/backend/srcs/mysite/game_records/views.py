from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OneOnOneMatch
from .serializers import OneOnOneMatchSerializer
from django.db.models import Q

# Create your views here.

# total match history
# "total_match_history": [
# {
#     "match_type": "배틀",
#     "total_match": 100,
#     "win": 50,
#     "lose": 50,
# }
# {
#     "match_type": "토너먼트",
#     "total_match": 100,
#     "1st": 25,
#     "2nd": 25,
#     "3rd": 25,
#     "4th": 25,
# }
# ],
# each match history
# "match_history": [
#       {
# 	      "date": [2025, 2, 7],
# 		    "match_type": "배틀",
# 		    "enemy": "seojilee",
# 		    "score": [4, 2], // my score가 배열의 시작
# 		    "result": "win",
#       },
#       {
# 	      "date": [2025, 2, 9],
# 		    "match_type": "토너먼트",
# 		    "rank": {
# 			    "1st": "seojilee",
# 			    "2nd": "taejeong",
# 			    "3rd": "hyoengsh",
# 			    "4th": "junhapar",
# 		    }
# 		    "result": 4,
#       },
# ],
class OneOnOneMatchViewSet(viewsets.ModelViewSet):
    queryset = OneOnOneMatch.objects.all()
    serializer_class = OneOnOneMatchSerializer

    # GET: READ
    @action(detail=False, methods=['get'], url_path='list')
    def get_matchlist(self, request):
        print('why are you here')
        user = request.user
        matches = OneOnOneMatch.objects.filter(Q(player1=user) | Q(player2=user))
        serializer = self.get_serializer(matches, many=True, context={"request": request})
        return Response(serializer.data)
