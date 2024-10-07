from django.db import models
from django.contrib.auth.models import AbstractUser

class Video(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField()
    
    def __str__(self):
        return f"{self.name} - {self.description} - {self.url}"

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=False, default=None, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    remember = models.BooleanField(default=False)
    provider = models.CharField(max_length=100, default=None, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']