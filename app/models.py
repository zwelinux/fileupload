from django.db import models
from django.conf import settings 
from django.contrib.auth.models import Group, User

class Idea(models.Model):
    title = models.CharField(max_length=255)
    powerpoint = models.FileField()
    note = models.TextField()
    share_to_gp = models.ManyToManyField(Group)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title