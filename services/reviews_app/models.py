from django.db import models
from django.conf import settings
from shop.models import Product

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # un usuario 1 sola reseña por producto
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} on {self.product}"
