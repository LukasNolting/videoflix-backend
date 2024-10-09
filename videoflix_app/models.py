from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    
    
    def __str__(self):
        return self.title

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=False, default=None, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    remember = models.BooleanField(default=False)
    provider = models.CharField(max_length=100, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Benutzer ist standardmäßig inaktiv

    USERNAME_FIELD = 'email'  # E-Mail wird als Benutzername verwendet
    REQUIRED_FIELDS = ['username']  # Username ist erforderlich

    def __str__(self):
        return self.email  # Optionale String-Repräsentation
