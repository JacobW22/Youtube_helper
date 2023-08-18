from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

import datetime

User._meta.get_field('email')._unique = True
    
class user_data_storage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    download_history = ArrayField(ArrayField(models.CharField(max_length=200), default=None))
    prompts_history = ArrayField(ArrayField(models.CharField(max_length=500), default=None))
    filtered_comments_history = ArrayField(ArrayField(models.CharField(max_length=200), default=None))
    transferred_playlists_history = ArrayField(ArrayField(models.CharField(max_length=200), default=None))

    save_history = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User's Storage"
        verbose_name_plural = "User's Storage"

    def __str__(self):
        return str(self.user)


class Ticket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    remaining_tickets = models.PositiveIntegerField(default=3)
    last_reset_time = models.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc).replace(hour=0,minute=0,second=0,microsecond=0))

    class Meta:
        verbose_name = "User's Tickets"
        verbose_name_plural = "User's Tickets"

    def __str__(self):
        return str(self.user)