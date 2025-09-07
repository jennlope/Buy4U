from django.urls import path

from .views import CreateReviewView

urlpatterns = [
    path(
        "shop/product/<int:id>/review/",
        CreateReviewView.as_view(),
        name="product_review",
    ),
]
