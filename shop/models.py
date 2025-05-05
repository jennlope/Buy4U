from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=255)
    warranty = models.CharField(max_length=255)
    description = models.TextField(verbose_name=_("Description"))
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    quantity = models.IntegerField(default=0)
    type = models.CharField(max_length=255, default="Electrónico")

    def __str__(self):
        return self.name