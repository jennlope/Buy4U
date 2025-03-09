from django.urls import path
from .views import HomePageView, ShopView, ProductDetailView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
]