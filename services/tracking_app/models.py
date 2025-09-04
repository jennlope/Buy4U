from django.db import models
from django.conf import settings

class Event(models.Model):
    EVENT_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('purchase', 'Purchase'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_TYPES)
    product_id = models.IntegerField(null=True, blank=True)
    path = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        who = self.user_id or self.session_key
        return f"{self.event_type} - {who} - {self.product_id}"
