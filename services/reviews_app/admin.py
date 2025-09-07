from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "created_at")
    search_fields = ("product__name", "user__username", "text")
    list_filter = ("created_at",)
