from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Event


def _safe_products(instance):
    """
    Devuelve una lista de productos (ids y nombres) asociados a la orden.
    No falla si aún no hay items.
    """
    products = []
    # Si existe el related_name "product_orders", lo usamos:
    try:
        for po in instance.product_orders.select_related("product").all():
            products.append(
                {
                    "product_id": getattr(
                        po.product, "id", getattr(po.product, "pk", None)
                    ),
                    "name": getattr(po.product, "name", None),
                    "quantity": getattr(po, "quantity", 1),
                }
            )
    except Exception:
        # Si todavía no hay items o el related_name cambia, devolvemos lista vacía
        pass
    return products


try:
    Order = apps.get_model("orders", "Order")
except Exception:
    Order = None

if Order:

    @receiver(post_save, sender=Order)
    def log_purchase(sender, instance, created, **kwargs):
        """
        Registra un evento 'purchase'.
        - Usa instance.pk / instance.order_id como identificador.
        - No depende de user (se registra como None).
        - Incluye productos en metadata cuando existan.
        - Evita duplicar si ya existe un Event con mismo order_id.
        """
        order_pk = instance.pk  # equivale a order_id en tu modelo
        order_id = getattr(instance, "order_id", order_pk)
        status = getattr(instance, "status", None)

        # Evitar duplicados: si ya hay un Event para esta orden, no vuelvas a crearlo.
        already = Event.objects.filter(
            event_type="purchase", metadata__order_id=order_id
        ).exists()
        if already and not created:
            return

        Event.objects.create(
            user=None,  # tu modelo Order no tiene user
            session_key=None,
            event_type="purchase",
            product_id=None,  # se documentan en metadata
            path="orders:process_payment",
            metadata={
                "order_pk": order_pk,
                "order_id": order_id,
                "status": status,
                "products": _safe_products(instance),
            },
        )
