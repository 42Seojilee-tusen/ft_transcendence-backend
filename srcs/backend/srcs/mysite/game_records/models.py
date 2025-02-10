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
    round1_player1 = models.ForeignKey(CustomUser, related_name="round1_player1_match", on_delete=models.CASCADE)
    round1_player2 = models.ForeignKey(CustomUser, related_name="round1_player2_match", on_delete=models.CASCADE)
    round1_point1 = models.IntegerField(default=0, null=False, blank=False)
    round1_point2 = models.IntegerField(default=0, null=False, blank=False)
    round2_player1 = models.ForeignKey(CustomUser, related_name="round2_player1_match", on_delete=models.CASCADE)
    round2_player2 = models.ForeignKey(CustomUser, related_name="round2_player2_match", on_delete=models.CASCADE)
    round2_point1 = models.IntegerField(default=0, null=False, blank=False)
    round2_point2 = models.IntegerField(default=0, null=False, blank=False)
    round3_player1 = models.ForeignKey(CustomUser, related_name="round3_player1_match", on_delete=models.CASCADE)
    round3_player2 = models.ForeignKey(CustomUser, related_name="round3_player2_match", on_delete=models.CASCADE)
    round3_point1 = models.IntegerField(default=0, null=False, blank=False)
    round3_point2 = models.IntegerField(default=0, null=False, blank=False)
    round4_player1 = models.ForeignKey(CustomUser, related_name="round4_player1_match", on_delete=models.CASCADE)
    round4_player2 = models.ForeignKey(CustomUser, related_name="round4_player2_match", on_delete=models.CASCADE)
    round4_point1 = models.IntegerField(default=0, null=False, blank=False)
    round4_point2 = models.IntegerField(default=0, null=False, blank=False)
    match_day = models.DateTimeField(auto_now_add=True)

class UserOneOnOneGameRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    one_on_one_match_id = models.ForeignKey(OneOnOneMatch, null=False, on_delete=models.CASCADE)
    
class UserTournamentGameRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tournament_match_id = models.ForeignKey(TournamentMatch, null=False, on_delete=models.CASCADE)
