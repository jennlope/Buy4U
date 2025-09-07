from django.contrib import admin

from .models import Product


@admin.register(Product)
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "brand",
        "warranty",
        "description",
        "image",
        "quantity",
        "type",
    )
    list_filter = ("brand", "warranty")
    search_fields = ("name", "brand")
