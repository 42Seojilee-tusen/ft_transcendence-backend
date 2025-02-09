from django.db import models
from users.models import CustomUser

class OneOnOneMatch(models.Model):
    id = models.BigAutoField(primary_key=True)
    player1 = models.ForeignKey(CustomUser, related_name="player1_match", on_delete=models.CASCADE)
    player2 = models.ForeignKey(CustomUser, related_name="player2_match", on_delete=models.CASCADE)
    point1 = models.IntegerField(default=0, null=False, blank=False)
    point2 = models.IntegerField(default=0, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def match_type(self):
        return "배틀"

    @property
    def enemy(self, player):
        return player1 if player != player1 else player2

    @property
    def score(self, player):
        return [point1, point2] if player == player1 else [point2, point1]

    @property
    def result(self, player):
        if self.point1 == self.point2:
            return "tie"
        winner = self.player1 if self.point1 > self.point2 else self.player2
        return "win" if winner == player else "lose"

class TournamentMatch(models.Model):
    id = models.BigAutoField(primary_key=True)
    one_on_one_match_id = models.ForeignKey(OneOnOneMatch, null=True, on_delete=models.CASCADE)
    tournament = models.IntegerField(null=False, blank=False)
    round = models.IntegerField(null=False, blank=False)
    match_day = models.DateTimeField(auto_now_add=True)

class UserGameRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    one_on_one_match_id = models.ForeignKey(OneOnOneMatch, null=True, on_delete=models.CASCADE)
    tournament_match_id = models.ForeignKey(TournamentMatch, null=True, on_delete=models.CASCADE)
