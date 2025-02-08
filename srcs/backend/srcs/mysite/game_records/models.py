from django.db import models
from users.models import CustomUser

class OneOnOneMatch(models.Model):
    id = models.BigAutoField(primary_key=True)
    player1 = models.ForeignKey(CustomUser, related_name="player1_match", on_delete=models.CASCADE)
    player2 = models.ForeignKey(CustomUser, related_name="player2_match", on_delete=models.CASCADE)
    point1 = models.IntegerField(default=0, null=False, blank=False)
    point2 = models.IntegerField(default=0, null=False, blank=False)
    match_day = models.DateTimeField(auto_now_add=True)

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