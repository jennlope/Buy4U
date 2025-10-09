from django.urls import path, re_path

from .views import (CartRemoveView, CartUpdateQuantityView, CartView,
                    GenerarReporteView, HomePageView, ProductDetailView,
                    ProductosAliadosView, ShopView, admin_product_view)
from .views import ReportsOverviewView, reports_data_json, reports_top_json, export_reports_csv

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("shop/", ShopView.as_view(), name="shop"),
    path("shop/product/<int:id>/", ProductDetailView.as_view(), name="product_detail"),
    path("cart/", CartView.as_view(), name="cart_index"),
    path("cart/add/<int:product_id>/", CartView.as_view(), name="add_cart"),
    path("cart/remove/<int:product_id>/", CartRemoveView.as_view(), name="remove_cart"),
    path(
        "cart/update/<int:product_id>/",
        CartUpdateQuantityView.as_view(),
        name="cart_update_quantity",
    ),
    path("admin_product/", admin_product_view.as_view(), name="admin_dashboard"),
        # Ruta adicional que acepta sin slash (para evitar 301 en tests que piden /admin_product)
    re_path(r'^admin_product/?$', admin_product_view.as_view(), name='admin_product_noslash'),
    path(
        "admin_product/generar_reporte/<str:tipo>/",
        GenerarReporteView.as_view(),
        name="generar_reporte",
    ),
    path(
        "productos-aliados/", ProductosAliadosView.as_view(), name="productos_aliados"
    ),
]

urlpatterns += [
    path("admin/reports/", ReportsOverviewView.as_view(), name="admin_reports_overview"),
    path("admin/reports/data/", reports_data_json, name="admin_reports_data_json"),
    path("admin/reports/top/", reports_top_json, name="admin_reports_top_json"),
    path("admin/reports/export_csv/", export_reports_csv, name="admin_reports_export_csv"),
]