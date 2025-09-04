from django.urls import path
from .views import DoAnOrderView, OrderConfirmationView, PaymentGatewayView, ProcessPaymentView, OrderStatusView,PurchaseHistoryView
 

urlpatterns = [
    path('Do_Order/', DoAnOrderView.as_view(), name='Do_Order'),
    path('order_confirmation/<int:order_id>/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('payment_gateway/', PaymentGatewayView.as_view(), name='payment_gateway'),
    path('process_payment/', ProcessPaymentView.as_view(), name='process_payment'),
    path('order_status/', OrderStatusView.as_view(), name='order_status'),  
    path('history/', PurchaseHistoryView.as_view(), name='order_history'), # Nueva ruta
]