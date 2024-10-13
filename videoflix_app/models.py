from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

def video_upload_path(instance, filename):
    """
    Returns a path for storing video files on the file system.

    The path is determined by the title of the video, with the title
    being converted to a valid filename and truncated to 50 characters.
    The path will be `videos/<title>/<filename>`.

    :param instance: The Video model instance
    :param filename: The name of the file to be uploaded
    :return: The path to store the video file
    """
    title = instance.title.replace(' ', '_') 
    title = title[:50]  
    folder_path = f'videos/{title}' 
    return f'{folder_path}/{filename}' 

def video_thumbnail_path(instance, filename):
    """
    Returns a path for storing video files on the file system.

    The path is determined by the title of the video, with the title
    being converted to a valid filename and truncated to 50 characters.
    The path will be `videos/<title>/<filename>`.

    :param instance: The Video model instance
    :param filename: The name of the file to be uploaded
    :return: The path to store the video file
    """
    title = instance.title.replace(' ', '_') 
    title = title[:50]  
    folder_path = f'videos/{title}' 
    return f'{folder_path}/{filename}' 


class Video(models.Model):
        CATEGORY_CHOICES = [
        ('new', 'New'),
        ('sci-fi', 'Sci-Fi'),
        ('horror', 'Horror'),
        ('action', 'Action'),
        ('drama', 'Drama'),
        ('comedy', 'Comedy'),
        ('documentary', 'Documentary'),
    ]
        title = models.CharField(max_length=100)
        description = models.TextField(max_length=1000)
        category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='new')
        created_at = models.DateTimeField(default=timezone.now)
        video_file = models.FileField(upload_to=video_upload_path, blank=True, null=True)
        thumbnail = models.ImageField(upload_to=video_thumbnail_path, blank=True, null=True)
        #possible to create thumbnail from video file and upload to thumbnails folder?
        #recently watched
        #recently watched current player time when stopped
        def __str__(self):
            return self.title

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=False, default=None, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    remember = models.BooleanField(default=False)
    provider = models.CharField(max_length=100, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=False)  # Benutzer ist standardmäßig inaktiv

    USERNAME_FIELD = 'email'  # E-Mail wird als Benutzername verwendet
    REQUIRED_FIELDS = ['username']  # Username ist erforderlich

    def __str__(self):
        return self.email  # Optionale String-Repräsentation

<<<<<<< HEAD
# todo : 
# class UserVideoModel
# -->start at last stopped time when playing
# class UserFavoriteModel
=======


class PasswordReset(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
>>>>>>> 0d9691ffcfe3de3cb678d6a1fed66a37e8f286fc
