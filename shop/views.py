from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect 
from django.views.generic import TemplateView, ListView
from django.views import View
from django import forms
from django.urls import reverse
from .models import Product

# Create your views here.
class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class ShopPageView(TemplateView):
    template_name = 'pages/shop.html'

class ShopView(View):
    template_name = 'pages/shop.html'

    def get(self, request):
        products = Product.objects.all()
        view_data = {
            "title": "Shop - Buy4U",
            "subtitle": "List of products",
            "products": products
        }
        return render(request, self.template_name, view_data)

class ProductDetailView(View):
    template_name = 'pages/product_detail.html'

    def get(self, request, id):
        try:
            product_id = int(id)
            if product_id < 1:
                raise ValueError("El ID de producto debe ser 1 o mayor")
            product = get_object_or_404(Product, pk=product_id)
        except (ValueError, IndexError):
            return HttpResponseRedirect(reverse('home'))

        view_data = {
            "title": product.name + " - Buy4U",
            "subtitle": product.name + " - Product information",
            "product": product
        }
        return render(request, self.template_name, view_data)