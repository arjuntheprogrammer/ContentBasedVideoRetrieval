from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class Video(models.Model):
    date_added = models.DateTimeField(default=timezone.now, null=True, blank=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    videoFile = models.FileField(upload_to="videos/", blank=True, null=True)
    data = JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.title
