# notifications/models.py
from django.db import models
from django.utils import timezone

class Notification(models.Model):
    type = models.CharField(max_length=50)
    message = models.TextField()
    cible = models.CharField(max_length=50, default="admin")
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} - {self.message[:40]}"
