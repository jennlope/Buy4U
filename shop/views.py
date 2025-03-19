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
    name = forms.CharField(required=False, label='Name', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'Search product'}))
    min_price = forms.DecimalField(required=False, label='Minimum price', min_value=0,widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum'}))
    max_price = forms.DecimalField(required=False, label='Maximum price', min_value=0,widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum'}))
    brand = forms.CharField(required=False, label='Brand',widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand'}))
    
    type = forms.ChoiceField(
        choices=[],required=False,label="Type",widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        types = Product.objects.values_list('type', flat=True).distinct()
        self.fields['type'].choices = [('', 'All')] + [(t, t) for t in types]

    
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
            type = form.cleaned_data.get('type')

            if name:
                products = products.filter(name__icontains=name)
            if min_price is not None:
                products = products.filter(price__gte=min_price)
            if max_price is not None:
                products = products.filter(price__lte=max_price)
            if brand:
                products = products.filter(brand__icontains=brand)
            if type:
                products = products.filter(type__iexact=type)

        view_data = {
            "title": "Shop - Buy4U",
            "subtitle": "List of products",
            "products": products,
            "form": form, 
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

        for product_id, quantity in cart_products_data.items():
            product = get_object_or_404(Product, id=int(product_id))
            cart_products[product] = quantity

        # Data for the view
        view_data = {
            "title": "Cart - Buy4U",
            "subtitle": "Shopping cart",
            "cart_products": cart_products,
        }
        return render(request, self.template_name, view_data)
    
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')
        
        cart_product_data = request.session.get('cart_product_data', {})
        
        quantity = int(request.POST.get("quantity", 1))
        
        if str(product_id) in cart_product_data:
            cart_product_data[str(product_id)] += quantity
        else:
            cart_product_data[str(product_id)] = quantity
            
        
        request.session['cart_product_data'] = cart_product_data
        return redirect('cart_index')
  
class CartUpdateQuantityView(View):
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')

        cart_product_data = request.session.get('cart_product_data', {})

        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            cart_product_data[str(product_id)] = quantity
        else:
            del cart_product_data[str(product_id)]  # Elimina si la cantidad es 0

        request.session['cart_product_data'] = cart_product_data
        return redirect('cart_index')
  
class CartRemoveView(View):
    template_name = 'cart/cart.html'

    def post (self, request, product_id):
        if not request.user.is_authenticated:
            return redirect('login')
        cart_product_data = request.session.get('cart_product_data', {})
        product_id = str(product_id)

        if product_id in cart_product_data:
            del cart_product_data[str(product_id)]
            request.session['cart_product_data'] = cart_product_data
        return redirect('cart_index')
    
def cart_count(request):
    cart_count = len(request.session.get('cart_product_data', {}))
    return {'cart_count': cart_count}

class admin_product_view(View):
    template_name = 'admin/manage.html'
    
    def get(self, request):
        products = Product.objects.all()
        view_data = {
            "title": "Admin - Buy4U",
            "subtitle": "Manage products",
            "products": products,
        }
        return render(request, self.template_name, view_data)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.POST.get('delete'):
            product_id = request.POST.get('delete')
            product = get_object_or_404(Product, pk=product_id)
            product.delete()
            return redirect('admin_dashboard')
        
        if request.POST.get('add'):
            name = request.POST.get('name')
            price = request.POST.get('price')
            brand = request.POST.get('brand')
            warranty = request.POST.get('warranty')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            quantity = request.POST.get('quantity')
            type = request.POST.get('type')
            product = Product(name=name, price=price, brand=brand, warranty=warranty, description=description, image=image, quantity=quantity, type=type)
            product.save()
            return redirect('admin_dashboard')
        
        if request.POST.get('edit'):
            product_id = request.POST.get('edit')
            product = get_object_or_404(Product, pk=product_id)
            name = request.POST.get('name')
            price = request.POST.get('price')
            brand = request.POST.get('brand')
            warranty = request.POST.get('warranty')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            quantity = request.POST.get('quantity')
            type = request.POST.get('type')
            product.name = name
            product.price = price
            product.brand = brand
            product.warranty = warranty
            product.description = description
            product.image = image
            product.quantity = quantity
            product.type = type
            product.save()
            return redirect('admin_dashboard')
        return redirect('admin_dashboard')