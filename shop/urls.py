from django.urls import path
from .views import HomePageView, ShopView, ProductDetailView, CartView, CartRemoveView, admin_product_view, CartUpdateQuantityView, GenerarReporteView, ProductosAliadosView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('shop/product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart_index'),
    path('cart/add/<int:product_id>/', CartView.as_view(), name='add_cart'),
    path('cart/remove/<int:product_id>/', CartRemoveView.as_view(), name='remove_cart'),
    path("cart/update/<int:product_id>/", CartUpdateQuantityView.as_view(), name="cart_update_quantity"),
    path('admin_product/', admin_product_view.as_view(), name='admin_dashboard'),
    path('admin_product/generar_reporte/<str:tipo>/', GenerarReporteView.as_view(), name='generar_reporte'),
    path('productos-aliados/',ProductosAliadosView.as_view(),name='productos_aliados'),]