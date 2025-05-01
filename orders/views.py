from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, Product, ProductOrder
from django.views import View
from django.urls import reverse

class DoAnOrderView(View):
    def post(self, request):
        cart_products = request.session.get('cart_product_data', {})

        if not cart_products:
            messages.error(request, "Oops! Your cart is currently empty.")
            return redirect('cart_index')
        
        return redirect(reverse('payment_gateway'))

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
        #Sacar los productos del carrito
        cart_products = request.session.get('cart_product_data', {})
        
        if not cart_products:
            messages.error(request, "Oops! Your cart is currently empty.")
            return redirect('cart_index')
        
        #Sabar los detalles de los productos y sumar el total
        products = []
        total = 0
        
        for product_id, quantity in cart_products.items():
            product = Product.objects.get(id=product_id)
            
            if product.quantity < int(quantity):
                messages.error(request, f"There is not enough stock for {product.name}. Only {product.quantity} available.")
                return redirect('cart_index')
            
            subtotal = product.price * int(quantity)
            total += subtotal
            products.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

        #Enviar datos a plantilla
        context = {
            'products': products,
            'total': total,
        }
        return render(request, 'pages/payment_gateway.html', context)        
    
class ProcessPaymentView(View):
    def post(self, request):
        #Aqui voy a redirigit los fuckings pagos, nada del otro mundo, algo sencillo
        #Sacar productos
        cart_products = request.session.get('cart_product_data', {})

        if not cart_products:
            messages.error(request, "Your cart is empty.")
            return redirect('cart_index')

        for product_id, quantity in cart_products.items():
            product = Product.objects.get(id=product_id)
            
            if product.quantity < int(quantity):
                messages.error(request, f"There is not enough stock for {product.name}. Only {product.quantity} available.")
                return redirect('cart_index')
            
            order = Order.objects.create()
            for product_id, quantity in cart_products.items():
                product = Product.objects.get(id=product_id)
                product.quantity -=int(quantity)
                product.save()
                #asocia los productos a la orden
                ProductOrder.objects.create(order=order, product=product, quantity=quantity)
                

        #Vaciar el carrito
        request.session['cart_product_data'] = {}
        #Volver a enviar a donde sale el pago
        messages.success(request, f"Order {order.order_id} has been successfully completed.")
        return redirect(reverse('order_confirmation', kwargs={'order_id': order.order_id}))
    
class OrderStatusView(View):
    def get(self, request):
        #Traer el estado del pago
        return render(request, 'pages/order_status.html')

    def post(self, request):
        #Sacar el numero de orden, el ID
        order_id = request.POST.get('order_id')

        try:
            #Buscar la orden
            order = Order.objects.get(order_id=order_id)
            return render(request, 'pages/order_status_result.html', {'order': order})
        except Order.DoesNotExist:
            #Error si no existe (Vo va a pasar)
            messages.error(request, "How did you even get here? Anyway, your order ID is not valid. Try another one, bro.")
            return redirect('order_status')