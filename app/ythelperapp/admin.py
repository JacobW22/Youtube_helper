from django.contrib import admin
from .models import user_data_storage, download_history_item, prompts_history_item, filtered_comments_history_item, transferred_playlists_history_item, Ticket


admin.site.register(user_data_storage)
admin.site.register(download_history_item)
admin.site.register(prompts_history_item)
admin.site.register(filtered_comments_history_item)
admin.site.register(transferred_playlists_history_item)
admin.site.register(Ticket)
