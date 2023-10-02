from django.db import models

# Create your models here.

class UserProfile(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    files_processed = models.IntegerField(default=0)