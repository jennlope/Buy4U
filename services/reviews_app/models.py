from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import Product


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user_name = models.CharField(max_length=255, blank=True, default='')  # Permitir blank y default
    comment = models.TextField(blank=True, default='')  # Permitir blank
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    useful_count = models.PositiveIntegerField(default=0)

    class Meta:
        # Remover unique_together ya que user puede ser null
        ordering = ["-created_at"]

    def __str__(self):
        display_name = self.user_name or (self.user.username if self.user else "Anonymous")
        return f"Review by {display_name} on {self.product}"
    
    def get_user_display_name(self):
        """Retorna el nombre a mostrar"""
        if self.user_name:
            return self.user_name
        return self.user.username if self.user else "Anonymous"
