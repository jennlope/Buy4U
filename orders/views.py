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
            order = Order.objects.get(order_id=order_id)
            return render(request, 'pages/order_confirmation.html', {'order': order})
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('shop')

class PaymentGatewayView(View):
    def get(self, request):
        # Obtener los productos del carrito desde la sesión
        cart_products = request.session.get('cart_product_data', {})
        
        # Obtener los detalles de los productos y calcular el total
        products = []
        total = 0
        for product_id, quantity in cart_products.items():
            product = Product.objects.get(id=product_id)
            subtotal = product.price * int(quantity)
            total += subtotal
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

        # Pasar los datos a la plantilla
        context = {
            'products': products,
            'total': total,
        }
        return render(request, 'pages/payment_gateway.html', context)        
    
class ProcessPaymentView(View):
    def post(self, request):
        # Simular el procesamiento del pago
        # Aquí podrías integrar una API de pago real, pero en este caso solo redirigimos

        # Obtener los productos del carrito desde la sesión
        cart_products = request.session.get('cart_product_data', {})

        if not cart_products:
            messages.error(request, "Your cart is empty.")
            return redirect('cart_index')

        # Crear la orden (esto ya lo tienes en DoAnOrderView)
        order = Order.objects.create()
        for product_id, quantity in cart_products.items():
            product = Product.objects.get(id=product_id)
            ProductOrder.objects.create(order=order, product=product, quantity=quantity)

        # Vaciar el carrito
        request.session['cart_product_data'] = {}

        # Redirigir a la página de confirmación del pedido
        messages.success(request, f"Order {order.order_id} successfully completed.")
        return redirect(reverse('order_confirmation', kwargs={'order_id': order.order_id}))