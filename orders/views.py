from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, Product, ProductOrder
from django.views import View
from django.urls import reverse

class DoAnOrderView(View):
    def post(self, request):
        cart_products = request.session.get('cart_product_data', {})

        if not cart_products:
            messages.error(request, "Your cart is empty.")
            return redirect('cart_index')

        order = Order.objects.create()
        for product_id, quantity in cart_products.items():
            product = Product.objects.get(id=product_id)
            
            # Verifica si el producto ya está en la orden
            order_product, created = ProductOrder.objects.get_or_create(order=order,product=product)
            
            if not created:
                # Si el producto ya estaba en la orden, actualiza la cantidad
                order_product.quantity += int(quantity)
                order_product.save()
            else:
                # Si es un nuevo producto, asigna la cantidad
                order_product.quantity = int(quantity)
                order_product.save()

        # Vaciar carrito
        request.session['cart_product_data'] = {}
        messages.success(request, f"Order {order.order_id} successfully completed.")
        
        return redirect(reverse('order_confirmation',kwargs={'order_id': order.order_id}))
# Create your views here.

class OrderConfirmationView(View):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            return render(request, 'pages/order_confirmation.html', {'order': order})
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('shop')