from django.urls import path
from .views import HomePageView, ShopView, ProductDetailView, CartView, CartRemoveView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart_index'),
    path('cart/add/<int:product_id>/', CartView.as_view(), name='add_cart'),
    path('cart/remove/<int:product_id>/', CartRemoveView.as_view(), name='remove_cart'),
]