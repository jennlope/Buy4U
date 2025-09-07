from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from shop.models import Product
from .forms import ReviewForm
from .models import Review
from .utils import user_purchased_product

class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, id=kwargs.get('id'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Review.objects.filter(product=self.product, user=self.request.user)

    def form_valid(self, form):
        # Validar que el usuario haya comprado
        if not user_purchased_product(self.request.user, self.product):
            messages.error(self.request, "Solo puedes reseñar productos que has comprado.")
            return redirect(reverse('product_detail', kwargs={'id': self.product.id}))

        # Evitar duplicado por unique_together
        if Review.objects.filter(product=self.product, user=self.request.user).exists():
            messages.info(self.request, "Ya has dejado una reseña para este producto.")
            return redirect(reverse('product_detail', kwargs={'id': self.product.id}))

        review = form.save(commit=False)
        review.user = self.request.user
        review.product = self.product
        review.save()
        messages.success(self.request, "¡Gracias por tu reseña!")
        return redirect(reverse('product_detail', kwargs={'id': self.product.id}))

    def form_invalid(self, form):
        messages.error(self.request, "Revisa el formulario de reseña.")
        return redirect(reverse('product_detail', kwargs={'id': self.product.id}))
