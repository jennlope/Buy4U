from django.db import models
from django.conf import settings

class BrowsingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    action = models.CharField(max_length=30)  # 'product_view' | 'search'
    product_id = models.IntegerField(null=True, blank=True)
    query = models.CharField(max_length=255, null=True, blank=True)
    path = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        what = self.product_id or self.query
        who = self.user_id or self.session_key
        return f"{self.action} - {who} - {what}"
