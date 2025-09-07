# services/reviews_app/urls.py
from django.urls import path
from .views import CreateReviewView

urlpatterns = [
    path("product/<int:id>/review/", CreateReviewView.as_view(), name="product_review"),
]
