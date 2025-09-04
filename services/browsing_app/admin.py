from django.contrib import admin
from .models import BrowsingHistory

@admin.register(BrowsingHistory)
class BrowsingHistoryAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'product_id', 'query', 'path', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('path', 'query')
