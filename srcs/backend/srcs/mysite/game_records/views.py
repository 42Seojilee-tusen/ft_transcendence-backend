from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import OneOnOneMatch
from .serializers import OneOnOneSerializer

# Create your views here.

class OneOnOneMatchViewSet(viewsets.ModelViewSet):
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
    queryset = OneOnOne.objects.all()
    serializer_class = OneOnOneSerializer

    # GET: READ
#    @action(detail=True, methods=['get'], url_path='list')
    def get_matchlist(self, request, pk=None):
        user = request.user
