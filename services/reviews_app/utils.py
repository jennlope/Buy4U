from orders.models import Order, ProductOrder

def user_purchased_product(user, product):
    if not user.is_authenticated:
        return False
    return ProductOrder.objects.filter(
        order__user=user,
        product=product
    ).exists()
