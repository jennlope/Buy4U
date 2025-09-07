from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "useful_count", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "product__name", "text")
