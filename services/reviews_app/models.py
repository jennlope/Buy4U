from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import Product


class Review(models.Model):
    product = models.ForeignKey("shop.Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()  # <-- DEBE EXISTIR
    useful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ["product", "user"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user_name} on {self.product}"
