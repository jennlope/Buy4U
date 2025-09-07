from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "user", "product_id", "path", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("path",)
