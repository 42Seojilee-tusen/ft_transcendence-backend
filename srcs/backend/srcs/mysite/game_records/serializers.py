# serializers.py
from rest_framework import serializers
from rest_framework.response import Response
from .models import OneOnOneMatch, UserOneOnOneGameRecord, TournamentMatch, UserTournamentGameRecord
from users.models import CustomUser

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
        return player1.username if player1 != user else player2.username

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
        model = TournamentMatch
        fields = ['date', 'match_type', 'enemy', 'result']

    # obj -> TournamentMatch
    def get_date(self, obj):
        date = obj.match_day
        return [date.year, date.month, date.day]

    def get_match_type(self, obj):
        return '토너먼트'

    def get_enemy(self, obj):
#        user = self.context.get('user')
       return {
               "player1": obj.round1_player1.username,
               "player2": obj.round1_player2.username,
               "player3": obj.round2_player1.username,
               "player4": obj.round2_player2.username
               }

    def get_result(self, obj):
        user = self.context.get('user')
        winner = obj.round3_player1 if obj.round3_point1 > obj.round3_point2 else obj.round3_player2
        if user != winner:
            return "lose"
        return "win"

class MatchHistorySerializer(serializers.ModelSerializer):
    total_match_history = serializers.SerializerMethodField()
    match_history = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['total_match_history', 'match_history']

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
        return sorted(one_on_one_serialized + tournament_serialized, key=lambda x: x["date"], reverse=True)

    def get_total_match_history(self, obj):
        one_on_one_games = UserOneOnOneGameRecord.objects.filter(user=obj)
        ooo_total_count = one_on_one_games.count()
        ooo_win_count = sum(
                1 for game in one_on_one_games
                if OneOnOneMatchSerializer(game.one_on_one_match_id, context={'user': obj}).get_result(game.one_on_one_match_id) == "win"
                )
        ooo_lose_count = ooo_total_count - ooo_win_count;
        one_on_one = {"match_type": "배틀", "total_match": ooo_total_count, "win": ooo_win_count, "lose": ooo_lose_count}

        tournament_games = UserTournamentGameRecord.objects.filter(user=obj)
        tour_total_count = tournament_games.count()
        tour_win_count = sum(
                1 for game in tournament_games
                if TournamentMatchSerializer(game.tournament_match_id, context={'user': obj}).get_result(game.tournament_match_id) == "win"
                )
        tour_lose_count = tour_total_count - tour_win_count
        tournament = {"match_type": "토너먼트", "total_match": tour_total_count, "win": tour_win_count, "lose": tour_lose_count}

        return [one_on_one, tournament]
