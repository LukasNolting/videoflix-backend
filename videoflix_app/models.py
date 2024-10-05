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
    password = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    remember = models.BooleanField(default=False)
    provider = models.CharField(max_length=100, default=None, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # This is important, as it's empty to prevent requiring 'username'

    # groups = models.ManyToManyField(
    #     'auth.Group',
    #     related_name='custom_user_set',
    #     blank=True,
    #     help_text='Die Gruppen, zu denen dieser Benutzer gehört.',
    #     verbose_name='Gruppen'
    # )
    # user_permissions = models.ManyToManyField(
    #     'auth.Permission',
    #     related_name='custom_user_permissions_set',
    #     blank=True,
    #     help_text='Spezifische Berechtigungen für diesen Benutzer.',
    #     verbose_name='Berechtigungen'
    # )