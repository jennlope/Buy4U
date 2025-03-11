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

class ProductFilterForm(forms.Form):
    name = forms.CharField(required=False, label='Name', widget=forms.TextInput(attrs={'placeholder': 'Buscar producto...'}))
    min_price = forms.DecimalField(required=False, label='Minimum price', min_value=0)
    max_price = forms.DecimalField(required=False, label='Maximum price', min_value=0)
    brand = forms.CharField(required=False, label='Brand')

class ShopView(View):
    template_name = 'pages/shop.html'

    def get(self, request):
        form = ProductFilterForm(request.GET)
        products = Product.objects.all()
        
        if form.is_valid():
            name = form.cleaned_data.get('name')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            brand = form.cleaned_data.get('brand')

            if name:
                products = products.filter(name__icontains=name)
            if min_price is not None:
                products = products.filter(price__gte=min_price)
            if max_price is not None:
                products = products.filter(price__lte=max_price)
            if brand:
                products = products.filter(brand__icontains=brand)

        view_data = {
            "title": "Shop - Buy4U",
            "subtitle": "List of products",
            "products": products,
            "form": form
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

class CartView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        # Extracting from the database the products available
        products = Product.objects.all()

        # Get cart items from session
        cart_products = {}
        cart_products_data = request.session.get('cart_product_data', {})

        for product in products:
            if str(product.id) in cart_products_data:
                cart_products[product.id] = product

        # Data for the view
        view_data = {
            "title": "Cart - Buy4U",
            "subtitle": "Shopping cart",
            "products": products,
            "cart_products": cart_products,
        }
        return render(request, self.template_name, view_data)
    
    def post(self, request, product_id):
        cart_product_data = request.session.get('cart_product_data', {})
        if product_id:
            cart_product_data[str(product_id)] = str(product_id)
            request.session['cart_product_data'] = cart_product_data

        return redirect('shop')
    
class CartRemoveView(View):
    template_name = 'cart/cart.html'

    def post (self, request, product_id):
        cart_product_data = request.session.get('cart_product_data', {})
        product_id = str(product_id)

        if product_id in cart_product_data:
            del cart_product_data[str(product_id)]
            request.session['cart_product_data'] = cart_product_data
        return redirect('cart_index')