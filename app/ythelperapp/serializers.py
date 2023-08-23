from rest_framework import serializers 
from .models import download_history_item, prompts_history_item, filtered_comments_history_item, transferred_playlists_history_item

class download_history_Serializer(serializers.ModelSerializer):
    class Meta:
        model = download_history_item
        exclude=('user',)

class prompts_history_Serializer(serializers.ModelSerializer):
    class Meta:
        model = prompts_history_item
        exclude=('user',)

class filtered_comments_history_Serializer(serializers.ModelSerializer):
    class Meta:
        model = filtered_comments_history_item
        exclude=('user',)

class transferred_playlists_history_Serializer(serializers.ModelSerializer):
    class Meta:
        model = transferred_playlists_history_item
        exclude=('user',)