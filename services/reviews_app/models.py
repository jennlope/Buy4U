from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import Product


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,  # ✅ ahora puede ser nulo
        blank=True  # ✅ también en formularios
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user_name = models.CharField(max_length=255)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    useful_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user_name} on {self.product}"
