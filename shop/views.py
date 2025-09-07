import requests
from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, TemplateView
from django.db.models import Avg, Count 
from services.reviews_app.forms import ReviewForm
from services.reviews_app.utils import user_purchased_product

# from .reportes import ReporteExcel, ReportePDF
from .models import Product


# Create your views here.
class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        weather = WeatherService(api_key=settings.WEATHER_API_KEY).get_weather_data()
        context["weather"] = weather
        return context


class ShopPageView(TemplateView):
    template_name = "pages/shop.html"


class ProductFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        label=_("Name"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Search product")}
        ),
    )
    min_price = forms.DecimalField(
        required=False,
        label=_("Minimum price"),
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Minimum")}
        ),
    )
    max_price = forms.DecimalField(
        required=False,
        label=_("Maximum price"),
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": _("Maximum")}
        ),
    )
    brand = forms.CharField(
        required=False,
        label=_("Brand"),
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Brand")}
        ),
    )

    type = forms.ChoiceField(
        choices=[],
        required=False,
        label=_("Type"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        types = Product.objects.values_list("type", flat=True).distinct()
        self.fields["type"].choices = [("", _("All"))] + [(t, t) for t in types]


class ShopView(View):
    template_name = "pages/shop.html"

    def get(self, request):
        form = ProductFilterForm(request.GET)
        products = Product.objects.all()

        if form.is_valid():
            name = form.cleaned_data.get("name")
            min_price = form.cleaned_data.get("min_price")
            max_price = form.cleaned_data.get("max_price")
            brand = form.cleaned_data.get("brand")
            type = form.cleaned_data.get("type")

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
            "title": _("Shop - Buy4U"),
            "subtitle": _("List of products"),
            "products": products,
            "form": form,
        }
        return render(request, self.template_name, view_data)


class ProductDetailView(View):
    template_name = "pages/product_detail.html"

    def get(self, request, id):
        try:
            product_id = int(id)
            if product_id < 1:
                raise ValueError(_("The product ID must be greater than or equal to 1."))
            product = get_object_or_404(Product, pk=product_id)
        except (ValueError, IndexError):
            return HttpResponseRedirect(reverse("home"))

        # ⬇️ ORDENAMIENTO
        sort = request.GET.get("sort", "recent")
        if sort == "rating":
            reviews_qs = product.reviews.select_related("user").order_by("-rating", "-created_at")
        elif sort == "useful":
            reviews_qs = product.reviews.select_related("user").order_by("-useful_count", "-created_at")
        else:
            # recent (default)
            reviews_qs = product.reviews.select_related("user").order_by("-created_at")

        can_review = user_purchased_product(request.user, product)
        review_form = ReviewForm() if can_review else None

        view_data = {
            "title": product.name + _(" - Buy4U"),
            "subtitle": product.name + _(" - Product information"),
            "product": product,
            "reviews": reviews_qs,
            "can_review": can_review,
            "review_form": review_form,
            "sort": sort,
        }

        avg = product.reviews.aggregate(avg=Avg("rating"), total=Count("id"))
        view_data["avg_rating"] = avg["avg"] or 0
        view_data["reviews_count"] = avg["total"] or 0
        return render(request, self.template_name, view_data)

class CartView(View):
    template_name = "cart/cart.html"

    def get(self, request):
        # Extracting from the database the products available
        products = Product.objects.all()

        # Get cart items from session
        cart_products = {}
        cart_products_data = request.session.get("cart_product_data", {})

        for product_id, quantity in cart_products_data.items():
            product = get_object_or_404(Product, id=int(product_id))
            cart_products[product] = quantity

        # Data for the view
        view_data = {
            "title": _("Cart - Buy4U"),
            "subtitle": _("Shopping cart"),
            "cart_products": cart_products,
        }
        return render(request, self.template_name, view_data)

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect("login")

        cart_product_data = request.session.get("cart_product_data", {})

        quantity = int(request.POST.get("quantity", 1))

        if str(product_id) in cart_product_data:
            cart_product_data[str(product_id)] += quantity
        else:
            cart_product_data[str(product_id)] = quantity

        request.session["cart_product_data"] = cart_product_data
        return redirect("cart_index")


class CartUpdateQuantityView(View):
    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect("login")

        cart_product_data = request.session.get("cart_product_data", {})

        quantity = int(request.POST.get("quantity", 1))
        if quantity > 0:
            cart_product_data[str(product_id)] = quantity
        else:
            del cart_product_data[str(product_id)]  # Elimina si la cantidad es 0

        request.session["cart_product_data"] = cart_product_data
        return redirect("cart_index")


class CartRemoveView(View):
    template_name = "cart/cart.html"

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return redirect("login")
        cart_product_data = request.session.get("cart_product_data", {})
        product_id = str(product_id)

        if product_id in cart_product_data:
            del cart_product_data[str(product_id)]
            request.session["cart_product_data"] = cart_product_data
        return redirect("cart_index")


def cart_count(request):
    cart_count = len(request.session.get("cart_product_data", {}))
    return {"cart_count": cart_count}


class admin_product_view(View):
    template_name = "admin/manage.html"

    def get(self, request):
        products = Product.objects.all()
        view_data = {
            "title": _("Admin - Buy4U"),
            "subtitle": _("Manage products"),
            "products": products,
        }
        return render(request, self.template_name, view_data)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.POST.get("delete"):
            product_id = request.POST.get("delete")
            product = get_object_or_404(Product, pk=product_id)
            product.delete()
            return redirect("admin_dashboard")

        if request.POST.get("add"):
            name = request.POST.get("name")
            price = request.POST.get("price")
            brand = request.POST.get("brand")
            warranty = request.POST.get("warranty")
            description = request.POST.get("description")
            image = request.FILES.get("image")
            quantity = request.POST.get("quantity")
            type = request.POST.get("type")
            product = Product(
                name=name,
                price=price,
                brand=brand,
                warranty=warranty,
                description=description,
                image=image,
                quantity=quantity,
                type=type,
            )
            product.save()
            return redirect("admin_dashboard")

        if request.POST.get("edit"):
            product_id = request.POST.get("edit")
            product = get_object_or_404(Product, pk=product_id)
            name = request.POST.get("name")
            price = request.POST.get("price")
            brand = request.POST.get("brand")
            warranty = request.POST.get("warranty")
            description = request.POST.get("description")
            image = request.FILES.get("image")
            quantity = request.POST.get("quantity")
            type = request.POST.get("type")
            product.name = name
            product.price = price
            product.brand = brand
            product.warranty = warranty
            product.description = description
            product.image = image
            product.quantity = quantity
            product.type = type
            product.save()
            return redirect("admin_dashboard")
        return redirect("admin_dashboard")


class WeatherService:
    def __init__(self, api_key, city=_("Medellin,CO")):
        self.api_key = api_key
        self.city = city

    def get_weather_data(self):
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={self.city}&units=metric&appid={self.api_key}&lang=en"
        )

        try:
            response = requests.get(url)
            data = response.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            icon = data["weather"][0]["icon"]

            # Diccionario de traducciones
            translations = {
                "clear sky": _("Clear sky"),
                "few clouds": _("Few clouds"),
                "scattered clouds": _("Scattered clouds"),
                "broken clouds": _("Broken clouds"),
                "shower rain": _("Shower rain"),
                "rain": _("Rain"),
                "thunderstorm": _("Thunderstorm"),
                "snow": _("Snow"),
                "mist": _("Mist"),
                "drizzle": _("Drizzle"),
                "overcast clouds": _("Overcast clouds"),
            }

            # Traducción de la descripción
            translated_desc = translations.get(desc.lower(), desc.capitalize())

            return {
                "temp": round(temp),
                "desc": translated_desc,
                "icon": f"http://openweathermap.org/img/wn/{icon}.png",
            }
        except:
            return {"temp": None, "desc": _("Unavailable"), "icon": ""}


# Api HU11  /productos-aliados.
class ProductosAliadosView(TemplateView):
    template_name = "pages/productos_aliados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            response = requests.get("http://buy4u.3utilities.com:8000/api/products/")
            context["productos"] = (
                response.json() if response.status_code == 200 else []
            )
        except Exception as e:
            context["productos"] = []
            print(_("The products could not be loaded"), e)
        return context


@method_decorator(staff_member_required, name="dispatch")
class GenerarReporteView(View):
    def get(self, request, tipo):
        from .reportes import ReporteExcel, ReportePDF

        queryset = Product.objects.all()

        if tipo == "excel":
            generador = ReporteExcel()
        elif tipo == "pdf":
            generador = ReportePDF()
        else:
            return HttpResponse(_("Invalid report type"), status=400)

        return generador.generar(queryset)
