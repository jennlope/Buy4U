from django.urls import path
from .views import DoAnOrderView, OrderConfirmationView  # Importa la vista

urlpatterns = [
    path('Do_Order/', DoAnOrderView.as_view(), name='Do_Order'),
    path('order_confirmation/<int:order_id>/', OrderConfirmationView.as_view(), name='order_confirmation'),
]
