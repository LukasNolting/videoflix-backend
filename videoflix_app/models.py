from django.db import models

class Video(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    url = models.URLField()
    
    def __str__(self):
        return f"{self.name} - {self.description} - {self.url}"
