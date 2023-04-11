from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

class user_data_storage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    download_history = ArrayField(ArrayField(models.CharField(max_length=200), default=None))