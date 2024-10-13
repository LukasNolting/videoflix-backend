from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

def video_upload_path(instance, filename):
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
        ('sci-fi', 'Sci-Fi'),
        ('horror', 'Horror'),
        ('action', 'Action'),
        ('drama', 'Drama'),
        ('animals', 'Animals'),
        ('documentary', 'Documentary'),
    ]
        title = models.CharField(max_length=100)
        description = models.TextField(max_length=1000)
        category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='new')
        created_at = models.DateTimeField(default=timezone.now)
        video_file = models.FileField(upload_to=video_upload_path, blank=True, null=True)
        thumbnail = models.ImageField(upload_to=video_thumbnail_path, blank=True, null=True)
        
        def __str__(self):
            return self.title

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=False, default=None, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    remember = models.BooleanField(default=False)
    provider = models.CharField(max_length=100, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class PasswordReset(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class UserFavoriteVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)