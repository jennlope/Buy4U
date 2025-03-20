from django.urls import path
from .views import DoAnOrderView, OrderConfirmationView, PaymentGatewayView, ProcessPaymentView

urlpatterns = [
    path('Do_Order/', DoAnOrderView.as_view(), name='Do_Order'),
    path('order_confirmation/<int:order_id>/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('payment_gateway/', PaymentGatewayView.as_view(), name='payment_gateway'),  # Nueva ruta
    path('process_payment/', ProcessPaymentView.as_view(), name='process_payment'),  # Nueva ruta
]