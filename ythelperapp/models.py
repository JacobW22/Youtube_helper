from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

User._meta.get_field('email')._unique = True
    
class user_data_storage(models.Model):
    object_name = models.CharField(max_length=255, default=None)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    download_history = ArrayField(ArrayField(models.CharField(max_length=200), default=None))
    prompts_history = ArrayField(ArrayField(models.CharField(max_length=500), default=None))
    filtered_comments_history = ArrayField(ArrayField(models.CharField(max_length=200), default=None))

    def __str__(self):
        return self.object_name


