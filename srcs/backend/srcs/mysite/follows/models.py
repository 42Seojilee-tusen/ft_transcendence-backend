from django.db import models
from users.models import CustomUser
# Create your models here.

class Follows(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    follow_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)