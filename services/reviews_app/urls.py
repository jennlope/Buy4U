
from django.urls import path
from .views import CreateReviewView, MarkReviewUsefulView

urlpatterns = [
    path("product/<int:id>/review/", CreateReviewView.as_view(), name="product_review"),
    path("reviews/<int:pk>/useful/", MarkReviewUsefulView.as_view(), name="review_useful"),
]
