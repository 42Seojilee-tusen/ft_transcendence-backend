from django.contrib.auth.models import AbstractUser
from django.db import models

class TCDUser(AbstractUser):
    id = models.IntegerField(primary_key=True)
    login = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(max_length=500)
    
    def __str__(self):
        return self.login
