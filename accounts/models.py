from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    GENDER_CHOICES = (("male","Male"),("female","Female"),("other","Other"))
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    country = models.CharField(max_length=80, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Profile {self.user.username}"
