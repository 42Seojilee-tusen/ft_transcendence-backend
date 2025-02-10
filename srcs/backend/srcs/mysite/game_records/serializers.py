# serializers.py
from rest_framework import serializers
from rest_framework.response import Response
from .models import OneOnOneMatch, UserOneOnOneGameRecord, TournamentMatch, UserTournamentGameRecord
from users.models import CustomUser

# {
#    "total_match_history": [
#	      { #		        "match_type": "배틀", #		        "total_match": 100,
#		        "win": 50,
#		        "lose": 50,
#	      }
#	      {
#		        "match_type": "토너먼트",
#		        "total_match": 100,
#		        "1st": 25,
#		        "2nd": 25,
#		        "3rd": 25,
#		        "4th": 25,
#	      }
#    ],
#    "match_history": [
#		    {
#		  	    "date": [2025, 2, 7],
#		        "match_type": "배틀",
#				"enemy": "seojilee",
#				"score": [4, 2], // my score가 배열의 시작
#				"result": "win",
#		    },
#		    {
#			    "date": [2025, 2, 9],
#				"match_type": "토너먼트",
#				"enemy": {
#					    "player1": "seojilee",
#					    "player2": "taejeong",
#					    "player3": "hyoengsh",
#					    "player4": "junhapar",
#				},
#				"result": "lose", // win or lose
#		    },
#    ],
#}
class OneOnOneMatchSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    match_type = serializers.SerializerMethodField()
    enemy = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = OneOnOneMatch
        fields = ['date', 'match_type', 'enemy', 'score', 'result']

    # obj -> OneOneOneMatch
    def get_date(self, obj):
        date = obj.match_day
        return [date.year, date.month, date.day]

    def get_match_type(self, obj):
        return '배틀'

    def get_enemy(self, obj):
        user = self.context.get('user')
        player1 = obj.player1
        player2 = obj.player2
        return player1.username if player1.username != user.username else player2.username

    def get_score(self, obj):
        user = self.context.get('user')
        return [obj.point1, obj.point2] if obj.player1 == user else [obj.point2, obj.point1]

    # no tie?
    def get_result(self, obj):
        user = self.context.get('user')
        return "win" if (user == obj.player1 and obj.point1 > obj.point2) or (user == obj.player2 and obj.point2 > obj.point1) else "lose"

class TournamentMatchSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    match_type = serializers.SerializerMethodField()
    enemy = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = OneOnOneMatch
        fields = ['date', 'match_type', 'enemy', 'score', 'result']

    # obj -> TournamentMatch
    def get_date(self, obj):
        date = obj.match_day
        return [date.year, date.month, date.day]

    def get_match_type(self, obj):
        return '토너먼트'

    def get_enemy(self, obj):
#        user = self.context.get('user')
       return {
               "player1": round1_player1,
               "player2": round1_player2,
               "player3": round2_player1,
               "player4": round2_player2
               }

    def get_result(self, obj):
        user = self.context.get('user')
        winner = round3_player1 if round3_point1 > round3_point2 else round3_player2
        if user != winner:
            return "lose"
        return "win"

class MatchHistorySerializer(serializers.ModelSerializer):
    match_history = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['match_history']

    # obj -> CustomUser
    def get_match_history(self, obj):
        one_on_one_games = UserOneOnOneGameRecord.objects.filter(user=obj)
        one_on_one_serialized = OneOnOneMatchSerializer(
            [record.one_on_one_match_id for record in one_on_one_games],
            many=True,
            context={'user': obj}
            ).data

        tournament_games = UserTournamentGameRecord.objects.filter(user=obj)
        tournament_serialized = TournamentMatchSerializer(
            [record.tournament_match_id for record in tournament_games],
            many=True,
            context={'user': obj}
            ).data
#        return one_on_one_serialized + tournament_serialized
        return sorted(one_on_one_serialized + tournament_serialized, key=lambda x: x["date"], reverse=True)
