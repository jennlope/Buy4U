from django.db import models
from shop.models import Product

# Create your models here.
class Order(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In_process'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Canceled'),
    ]
    order_id = models.AutoField(primary_key=True)
    products = models.ManyToManyField(Product, through='ProductOrder')
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.order_id} - Status: {self.status}"

class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="product_orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.order_id}"