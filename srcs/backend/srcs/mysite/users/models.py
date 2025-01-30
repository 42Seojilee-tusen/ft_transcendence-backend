from django.contrib.auth.models import AbstractUser
from django.db import models

class TCDUser(AbstractUser):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=100, blank=True)
    login = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(max_length=500)
    two_factor_secret_key = models.CharField(max_length=500, blank=True)
    two_factor_authorization = models.BooleanField(default=False)

    def __str__(self):
        return self.login
