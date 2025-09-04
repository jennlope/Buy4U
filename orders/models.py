# orders/models.py
from django.db import models
from django.conf import settings
from shop.models import Product

class Order(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pending'),
        ('in_process', 'In_process'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Canceled'),
    ]
    order_id = models.AutoField(primary_key=True)
    # 🔽 NUEVO: usuario dueño de la compra (opcional por compatibilidad)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders'
    )
    # 🔽 NUEVO: fecha de creación para ordenar cronológicamente
    created_at = models.DateTimeField(auto_now_add=True)

    products = models.ManyToManyField(Product, through='ProductOrder')
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.order_id} - Status: {self.status}"

    # (Opcional) total calculado, si Product tiene 'price'
    @property
    def total(self):
        try:
            return sum(po.product.price * po.quantity for po in self.product_orders.select_related('product'))
        except Exception:
            return None

class ProductOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="product_orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} in Order {self.order.order_id}"
