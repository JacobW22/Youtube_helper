from django.contrib import admin
from .models import user_data_storage, Ticket

admin.site.register(user_data_storage)
admin.site.register(Ticket)
