from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

User._meta.get_field('email')._unique = True
    

class user_data_storage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    save_history = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User's Storage"
        verbose_name_plural = "User's Storages"

    def __str__(self):
        return str(self.user)



class download_history_item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    saved_on = models.DateTimeField(default=timezone.now)
    thumbnail_url = models.CharField(max_length=255)

    class Meta:
        ordering = ['-id']
        verbose_name = "Download History Item"
        verbose_name_plural = "Download History Items"

    def __str__(self):
        return str(f'{self.user} {self.id}th item')


class prompts_history_item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    saved_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name = "Prompts History Item"
        verbose_name_plural = "Prompts History Items"

    def __str__(self):
        return str(f'{self.user} {self.id}th item')



class filtered_comments_history_item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    saved_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name = "Filtered Comments History Item"
        verbose_name_plural = "Filtered Comments History Items"

    def __str__(self):
        return str(f'{self.user} {self.id}th item')
    


class transferred_playlists_history_item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    title = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    saved_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name = "Transferred Playlists History Item"
        verbose_name_plural = "Transferred Playlists History Items"

    def __str__(self):
        return str(f'{self.user} {self.id}th item')



class Ticket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    remaining_tickets = models.PositiveIntegerField(default=3)
    last_reset_time = models.DateTimeField(default=timezone.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0))

    class Meta:
        verbose_name = "User's Tickets"
        verbose_name_plural = "User's Tickets"

    def __str__(self):
        return str(self.user)