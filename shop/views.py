import requests
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, TemplateView
from django.db.models import Avg, Count, F
from services.reviews_app.forms import ReviewForm
from services.reviews_app.utils import user_purchased_product
from services.browsing_app.models import BrowsingHistory
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

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
            query = request.GET.get('name', '').strip()
            if query:
                BrowsingHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=request.session.session_key,
                    action='search',
                    query=query,
                    path=request.get_full_path()
                )
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


import math

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

        # Calcular promedio y descomponerlo en estrellas completas, medias y vacías
        avg = product.reviews.aggregate(avg=Avg("rating"), total=Count("id"))
        avg_rating = avg["avg"] or 0
        reviews_count = avg["total"] or 0
        
        # Calcular estrellas: completas, media, vacías
        full_stars = int(math.floor(avg_rating))  # Estrellas completas
        has_half_star = (avg_rating - full_stars) >= 0.3  # Media estrella si decimal >= 0.3
        empty_stars = 5 - full_stars - (1 if has_half_star else 0)  # Resto vacías

        # 🔴 IMPORTANTE: Convertir QuerySet a lista para asegurar que se evalúe
        reviews_list = list(reviews_qs)
        
        view_data = {
            "title": product.name + _(" - Buy4U"),
            "subtitle": product.name + _(" - Product information"),
            "product": product,
            "reviews": reviews_list,
            "can_review": can_review,
            "review_form": review_form,
            "sort": sort,
            "avg_rating": avg_rating,
            "reviews_count": reviews_count,
            "full_stars": full_stars,
            "has_half_star": has_half_star,
            "empty_stars": empty_stars,
        }

        return render(request, self.template_name, view_data)

class CartView(View):
    template_name = "cart/cart.html"

    def get(self, request):
        # Extracting from the database the products available
        products = Product.objects.all()

        # Get cart items from session - USAR LA MISMA CLAVE
        cart_products = {}
        cart_product_data = request.session.get("cart_product_data", {})

        for product_id, quantity in cart_product_data.items():
            try:
                product = get_object_or_404(Product, id=int(product_id))
                cart_products[product] = quantity
            except:
                continue

        # Data for the view
        view_data = {
            "title": _("Cart - Buy4U"),
            "subtitle": _("Shopping cart"),
            "cart_products": cart_products,
        }
        return render(request, self.template_name, view_data)

    def post(self, request, product_id):
        try:
            product = get_object_or_404(Product, pk=product_id)
            
            # Verificar stock
            if product.quantity <= 0:
                messages.error(request, _("Este producto no está disponible"))
                return redirect("shop")
            
            # Incrementar contador de veces añadido
            Product.objects.filter(pk=product_id).update(times_added_to_cart=F('times_added_to_cart') + 1)
            
            # USAR LA MISMA CLAVE: cart_product_data
            cart_product_data = request.session.get("cart_product_data", {})
            quantity = int(request.POST.get("quantity", 1))
            
            # Convertir product_id a string para consistencia
            product_id_str = str(product_id)
            
            if product_id_str in cart_product_data:
                cart_product_data[product_id_str] += quantity
            else:
                cart_product_data[product_id_str] = quantity
            
            # Guardar en sesión
            request.session["cart_product_data"] = cart_product_data
            request.session.modified = True  # Forzar guardado
            
            messages.success(request, _("Product added to cart successfully"))
            return redirect("cart_index")
            
        except Product.DoesNotExist:
            messages.error(request, _("Product not found"))
            return redirect("shop")
        except Exception as e:
            messages.error(request, _("Error adding product to cart"))
            print(f"Error en CartView.post: {e}")  # Para debug
            return redirect("shop")

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

        # Default values (para evitar NameError en template)
        browsing_history_page = None
        browsing_users_page = None
        browsing_categories = []
        browsing_filters = {
            "user_id": "", "query": "", "action": "", "start": "", "end": "",
            "category": "", "country": "", "gender": ""
        }

        if request.user.is_staff:
            # Query inicial
            bh_qs = BrowsingHistory.objects.select_related("user").all().order_by("-created_at")

            # Leer filtros del GET
            user_id = request.GET.get("bh_user_id", "")
            query = request.GET.get("bh_query", "")
            action = request.GET.get("bh_action", "")
            start = request.GET.get("bh_start", "")
            end = request.GET.get("bh_end", "")
            category = request.GET.get("bh_category", "")
            country = request.GET.get("bh_country", "")
            gender = request.GET.get("bh_gender", "")

            # Aplicar filtros sobre browsing history
            if user_id:
                try:
                    bh_qs = bh_qs.filter(user_id=int(user_id))
                except ValueError:
                    pass

            if query:
                bh_qs = bh_qs.filter(query__icontains=query)

            if action:
                bh_qs = bh_qs.filter(action=action)

            if start:
                bh_qs = bh_qs.filter(created_at__date__gte=start)
            if end:
                bh_qs = bh_qs.filter(created_at__date__lte=end)

            # Filtrar por categoria (type en Product) si se especifica
            if category:
                from shop.models import Product as ShopProduct
                product_ids = ShopProduct.objects.filter(type__iexact=category).values_list("id", flat=True)
                bh_qs = bh_qs.filter(product_id__in=product_ids)

            # Filtrar por demografía (opcional) si existe perfil con esos campos
            User = get_user_model()
            try:
                sample_user = User.objects.first()
            except Exception:
                sample_user = None

            profile_has_country = False
            profile_has_gender = False
            if sample_user is not None and hasattr(sample_user, "profile"):
                prof = getattr(sample_user, "profile")
                profile_has_country = hasattr(prof, "country")
                profile_has_gender = hasattr(prof, "gender")

            if country and profile_has_country:
                user_ids = User.objects.filter(profile__country__iexact=country).values_list("id", flat=True)
                bh_qs = bh_qs.filter(user_id__in=user_ids)

            if gender and profile_has_gender:
                user_ids = User.objects.filter(profile__gender__iexact=gender).values_list("id", flat=True)
                bh_qs = bh_qs.filter(user_id__in=user_ids)

            # Export CSV si se solicita (respeta filtros ya aplicados)
            if request.GET.get("bh_export") == "csv":
                import csv
                from django.http import HttpResponse
                filename = "browsing_history_filtered.csv"
                resp = HttpResponse(content_type="text/csv")
                resp["Content-Disposition"] = f'attachment; filename="{filename}"'
                writer = csv.writer(resp)
                writer.writerow(["id", "user", "session_key", "action", "product_id", "query", "path", "created_at"])
                for b in bh_qs:
                    writer.writerow([b.id, b.user.username if b.user else "", b.session_key, b.action, b.product_id, b.query, b.path, b.created_at])
                return resp

            # Paginación historial
            from django.core.paginator import Paginator
            page_num = request.GET.get("bh_page", 1)
            paginator = Paginator(bh_qs, 20)
            browsing_history_page = paginator.get_page(page_num)

            # Lista de categorías (para el select)
            from shop.models import Product as ShopProduct
            browsing_categories = list(ShopProduct.objects.values_list("type", flat=True).distinct())

            # Lista de usuarios que aparecen en el historial (para select/paginador)
            bh_user_ids = BrowsingHistory.objects.values_list("user_id", flat=True).distinct()
            browsing_users_qs = User.objects.filter(id__in=[uid for uid in bh_user_ids if uid]).order_by("username")
            users_paginator = Paginator(browsing_users_qs, 10)
            bpage = request.GET.get("bpage", 1)
            browsing_users_page = users_paginator.get_page(bpage)

            # preparar filtros para el template
            browsing_filters = {
                "user_id": user_id, "query": query, "action": action,
                "start": start, "end": end, "category": category,
                "country": country, "gender": gender
            }

        # Añadir al contexto (sea staff o no)
        view_data.update({
            "browsing_history_page": browsing_history_page,
            "browsing_users_page": browsing_users_page,
            "browsing_categories": browsing_categories,
            "browsing_users_count": browsing_users_qs.count() if request.user.is_staff else 0,
            "browsing_filters": browsing_filters,
        })

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
    
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils import timezone
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
import csv
from datetime import timedelta, date

from services.browsing_app.models import BrowsingHistory
from services.reviews_app.models import Review
from shop.models import Product
from orders.models import Order  # ajusta el import si tu app/archivo se llama diferente

@method_decorator(staff_member_required, name='dispatch')
class ReportsOverviewView(TemplateView):
    template_name = "admin/reports.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        days = int(self.request.GET.get('days', 30))
        ctx['days'] = days
        # pasar today en formato ISO para inputs date / querystring
        ctx['today'] = timezone.localdate().isoformat()
        return ctx

@staff_member_required
def reports_data_json(request):
    # days param
    days = int(request.GET.get("days", 30))
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days-1)

    # Visits per day (BrowsingHistory action='product_view')
    visits_qs = (
        BrowsingHistory.objects
        .filter(action='product_view', created_at__date__gte=start_date, created_at__date__lte=end_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Purchases per day (Order) — cuenta por order_id porque tu modelo tiene ese campo
    purchases_qs = (
        Order.objects
        .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('order_id'))   # usa order_id tal como aparece en tu modelo
        .order_by('day')
    )

    # Avg rating per day (Review)
    ratings_qs = (
        Review.objects
        .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(avg_rating=Avg('rating'))
        .order_by('day')
    )

    # build a list of labels covering the full date range so chart.js siempre tenga todas las fechas
    labels = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        labels.append(d.isoformat())

    # helper dicts for quick lookup
    visits_map = {str(item['day']): item['count'] for item in visits_qs}
    purchases_map = {str(item['day']): item['count'] for item in purchases_qs}
    ratings_map = {str(item['day']): float(item['avg_rating']) if item['avg_rating'] is not None else None for item in ratings_qs}

    visits = [visits_map.get(lbl, 0) for lbl in labels]
    purchases = [purchases_map.get(lbl, 0) for lbl in labels]
    avg_ratings = [ratings_map.get(lbl, None) for lbl in labels]

    return JsonResponse({
        "labels": labels,
        "visits": visits,
        "purchases": purchases,
        "avg_ratings": avg_ratings,
    })



@staff_member_required
def reports_top_json(request):
    n = int(request.GET.get("n", 5))
    days = int(request.GET.get("days", 30))
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days-1)

    # Top viewed: contar BrowsingHistory por product_id
    top_viewed_qs = (
        BrowsingHistory.objects
        .filter(action='product_view', created_at__date__gte=start_date, created_at__date__lte=end_date, product_id__isnull=False)
        .values('product_id')
        .annotate(views=Count('id'))
        .order_by('-views')[:n]
    )
    product_ids_viewed = [item['product_id'] for item in top_viewed_qs]
    products_viewed = Product.objects.in_bulk(product_ids_viewed)
    top_viewed = []
    for item in top_viewed_qs:
        pid = item['product_id']
        p = products_viewed.get(pid)
        top_viewed.append({
            "product_id": pid,
            "product_name": p.name if p else "Unknown",
            "views": item['views'],
        })

    # Top bought: dependiendo de cómo almacenas order-product relation.
    # Si Order tiene M2M "products" o "product_orders" con qty, adapta la consulta.
    # Aquí asumo que hay una relación Order.products (m2m) o ProductOrder con order and product.
    # Intento contar por product en la tabla intermedia si existe:
    top_bought = []
    try:
        # Attempts for common patterns:
        # 1) if you have a through model `ProductOrder` with (order, product, quantity)
        from orders.models import ProductOrder  # ajusta nombre si es distinto
        bought_qs = (
            ProductOrder.objects
            .filter(order__created_at__date__gte=start_date, order__created_at__date__lte=end_date)
            .values('product_id')
            .annotate(qty=Count('id'))  # si hay campo quantity usa Sum('quantity')
            .order_by('-qty')[:n]
        )
        product_ids_bought = [i['product_id'] for i in bought_qs]
        products_bought = Product.objects.in_bulk(product_ids_bought)
        for it in bought_qs:
            pid = it['product_id']
            p = products_bought.get(pid)
            top_bought.append({
                "product_id": pid,
                "product_name": p.name if p else "Unknown",
                "qty": it['qty'],
            })
    except Exception:
        # Fallback: si no existe ProductOrder, intentamos contar orders.products (m2m)
        try:
            bought_qs = (
                Order.objects
                .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
                .values('products__id', 'products__name')
                .annotate(qty=Count('products__id'))
                .order_by('-qty')[:n]
            )
            for it in bought_qs:
                top_bought.append({
                    "product_id": it.get('products__id'),
                    "product_name": it.get('products__name') or "Unknown",
                    "qty": it.get('qty'),
                })
        except Exception:
            # No data source found — devolver vacío
            top_bought = []

    return JsonResponse({
        "top_viewed": top_viewed,
        "top_bought": top_bought,
    })


@staff_member_required
def export_reports_csv(request):
    days = int(request.GET.get("days", 30))
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=days-1)

    # build visits and purchases (simple rows)
    visits_qs = (
        BrowsingHistory.objects
        .filter(action='product_view', created_at__date__gte=start_date, created_at__date__lte=end_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(views=Count('id'))
        .order_by('day')
    )

    purchases_qs = (
        Order.objects
        .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(orders=Count('order_id'))
        .order_by('day')
    )

    # zip days together for CSV rows
    labels = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        labels.append(d.isoformat())

    visits_map = {str(x['day']): x['views'] for x in visits_qs}
    purchases_map = {str(x['day']): x['orders'] for x in purchases_qs}

    filename = f"reports_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(resp)
    writer.writerow(['date', 'visits', 'orders'])
    for lbl in labels:
        writer.writerow([lbl, visits_map.get(lbl, 0), purchases_map.get(lbl, 0)])

    return resp

from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(staff_member_required, name='dispatch')
class AdminReportsDataJson(View):
    def get(self, request):
        days = int(request.GET.get('days', 30))
        # Aquí calculas labels, visitas, compras, avg_ratings por día
        # Ejemplo ficticio:
        labels = ["2025-10-01","2025-10-02"]
        visits = [10, 12]
        purchases = [1, 3]
        avg_ratings = [4.2, 4.0]
        return JsonResponse({
            "labels": labels, "visits": visits, "purchases": purchases, "avg_ratings": avg_ratings
        })

@method_decorator(staff_member_required, name='dispatch')
class AdminReportsTopJson(View):
    def get(self, request):
        # consulta a BrowsingHistory y Orders para construir top
        # ejemplo mínimo:
        top_viewed = [{"product_name": "Phone X", "views": 42}]
        top_bought = [{"product_name": "Phone X", "qty": 10}]
        return JsonResponse({"top_viewed": top_viewed, "top_bought": top_bought})

# al inicio del fichero donde ya usas aggregates
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count, F
from django.db import connection
import csv
import statistics

# Intentamos importar StdDev (algunas DBs lo soportan)
try:
    from django.db.models import StdDev
except Exception:
    StdDev = None

# Model imports
from services.reviews_app.models import Review
from shop.models import Product


@login_required
@user_passes_test(lambda u: u.is_staff)
def rating_stats_json(request):
    top = request.GET.get("top")
    try:
        top = int(top)
    except (TypeError, ValueError):
        top = None

    qs = Review.objects.values(name=F("product__name")).annotate(
        avg_rating=Avg("rating"),
        reviews_count=Count("id"),
    ).order_by("-avg_rating")

    # intentar StdDev solo si DB lo soporta
    try:
        from django.db.models import StdDev
        qs = qs.annotate(stddev_rating=StdDev("rating"))
    except Exception:
        # en SQLite omitimos desviación
        qs = qs.annotate(stddev_rating=None)

    if top:
        qs = qs[:top]

    data = [{
        "name": r["name"],
        "avg_rating": round(r["avg_rating"], 2) if r["avg_rating"] else 0,
        "stddev_rating": round(r.get("stddev_rating") or 0, 2),
        "reviews_count": r["reviews_count"]
    } for r in qs]

    return JsonResponse({"rating_stats": data})

@staff_member_required
def rating_stats_page(request):
    """
    Página HTML que muestra tabla simple y link al CSV (usa fetch al JSON).
    Rutas: /admin/reports/ratings/
    """
    top = request.GET.get("top", "")
    context = {"top": top}
    return render(request, "admin/rating_stats.html", context)


##HU13
# arriba de todo en shop/views.py (reemplaza la import rota)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.db.models import Count, Sum
from django.apps import apps

from services.browsing_app.models import BrowsingHistory
from shop.models import Product

# obtiene el modelo OrderProduct de forma dinámica (evita ModuleNotFoundError si el nombre cambia)
OrderProduct = apps.get_model("orders", "ProductOrder") or apps.get_model("orders", "OrderProduct") or apps.get_model("orders", "ProductOrderModel")
# si tu proyecto usa otro nombre para la tabla intermedia ajusta el string anterior

@login_required
@user_passes_test(lambda u: u.is_staff)
def top_products_json(request):
    n = int(request.GET.get("n", 10))

    top_viewed_qs = (
        BrowsingHistory.objects
        .filter(action="product_view", product_id__isnull=False)
        .values("product_id")
        .annotate(views=Count("id"))
        .order_by("-views")[:n]
    )

    # maneja caso en que OrderProduct pueda no existir
    top_bought_list = []
    try:
        top_bought_qs = (
            OrderProduct.objects
            .values("product_id")
            .annotate(qty=Sum("quantity"))
            .order_by("-qty")[:n]
        )
    except Exception:
        top_bought_qs = []

    top_viewed_list = []
    for v in top_viewed_qs:
        product = Product.objects.filter(id=v["product_id"]).first()
        top_viewed_list.append({
            "product": product.name if product else "Unknown",
            "views": v["views"]
        })

    for b in top_bought_qs:
        product = Product.objects.filter(id=b["product_id"]).first()
        top_bought_list.append({
            "product": product.name if product else "Unknown",
            "qty": b.get("qty", 0)
        })

    return JsonResponse({"top_viewed": top_viewed_list, "top_bought": top_bought_list})


@login_required
@user_passes_test(lambda u: u.is_staff)
def top_products_page(request):
    return render(request, "admin/top_products.html")

##HU14
# al principio del archivo shop/views.py (imports principales)
import csv
import io
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count, F
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.apps import apps

# Import correcto del browsing history existente:
from services.browsing_app.models import BrowsingHistory

# Importa Product y Orders dinámicamente cuando lo necesites:
Product = apps.get_model('shop', 'Product')
# Order / OrderProduct pueden recogerse así:
try:
    OrderProduct = apps.get_model('orders', 'ProductOrder')  # o el nombre que uses
except LookupError:
    OrderProduct = None

from django.views import View
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

@method_decorator(staff_member_required, name="dispatch")
class GenerarReporteView(View):
    """
    Genera reportes básicos: CSV export con estadísticas de ventas y visitas.
    Rutas: /admin/reports/export/ (GET ?type=csv)
    """
    def get(self, request, tipo=None):
        # tipo puede ser 'excel' o 'pdf' o 'csv' según lo que envíes; por ahora soportamos csv de forma robusta
        report_type = request.GET.get('type', 'csv').lower()

        # Datos básicos: top productos por vistas y por compras
        # Top por vistas: usar BrowsingHistory (product_view)
        top_views = (BrowsingHistory.objects
                     .filter(action='product_view', product_id__isnull=False)
                     .values('product_id')
                     .annotate(views=Count('id'))
                     .order_by('-views')[:20])

        # Top por compras: intentar usar orders.ProductOrder o el modelo de pedidos
        top_bought = []
        if OrderProduct is not None:
            top_bought = (OrderProduct.objects
                          .values('product_id')
                          .annotate(qty=Count('pk'))
                          .order_by('-qty')[:20])
        else:
            # fallback: consultar orders app por relacion M2M si existe
            try:
                Order = apps.get_model('orders', 'Order')
                top_bought = (Order.objects
                              .values('product_orders__product_id')
                              .annotate(qty=Count('product_orders__id'))
                              .order_by('-qty')[:20])
            except Exception:
                top_bought = []

        # Si piden CSV, generar y devolver
        if report_type == 'csv':
            filename = "reporte_detallado.csv"
            resp = HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = f'attachment; filename="{filename}"'
            writer = csv.writer(resp)

            # Encabezado más claro
            writer.writerow(["Tipo", "Producto", "Métrica", "Valor"])

            # Mejorar: obtener nombres de productos
            product_names = {
                p.id: p.name for p in Product.objects.filter(
                    id__in=[
                        *[v["product_id"] for v in top_views],
                        *[b.get("product_id") or b.get("product_orders__product_id") for b in top_bought]
                    ]
                )
            }

            # Escribir vistas
            for tv in top_views:
                pid = tv.get("product_id")
                pname = product_names.get(pid, f"Producto {pid}")
                writer.writerow(["Visualizaciones", pname, "Vistas", tv.get("views")])

            # Escribir compras
            for tb in top_bought:
                pid = tb.get("product_id") or tb.get("product_orders__product_id")
                pname = product_names.get(pid, f"Producto {pid}")
                val = tb.get("qty") or tb.get("qty", "")
                writer.writerow(["Compras", pname, "Cantidad", val])

            return resp


        # Para otros tipos (excel/pdf) se puede delegar a librerías, pero por ahora mostramos JSON con datos
        return JsonResponse({
            'top_views': list(top_views),
            'top_bought': list(top_bought),
        })

@method_decorator(staff_member_required, name='dispatch')
class MostAddedToCartView(View):
    """HU15: Productos más añadidos al carrito"""
    template_name = "admin/most_added_to_cart.html"
    
    def get(self, request):
        # Obtener productos ordenados por veces añadidos
        products = Product.objects.filter(
            times_added_to_cart__gt=0
        ).order_by('-times_added_to_cart')[:20]
        
        # Calcular porcentaje del más añadido
        max_count = products.first().times_added_to_cart if products else 1
        
        products_data = []
        for product in products:
            percentage = (product.times_added_to_cart / max_count * 100) if max_count > 0 else 0
            products_data.append({
                'product': product,
                'count': product.times_added_to_cart,
                'percentage': percentage
            })
        
        context = {
            'title': _('Productos más añadidos al carrito'),
            'products_data': products_data,
            'total_products': products.count()
        }
        
        return render(request, self.template_name, context)

from django.http import JsonResponse
from .ai_service import GeminiService
from django.views.decorators.http import require_http_methods
import json

# HU18: Recomendación de precios con IA
@staff_member_required
@require_http_methods(["POST"])
def recomendar_precio_producto(request):
    """
    Endpoint para recomendar precio usando Gemini AI
    """
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '')
        marca = data.get('marca', '')
        tipo = data.get('tipo', '')
        
        if not nombre:
            return JsonResponse({
                "success": False,
                "error": "El nombre del producto es requerido"
            }, status=400)
        
        gemini_service = GeminiService()
        resultado = gemini_service.recomendar_precio(nombre, marca, tipo)
        
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


# HU17: Comparación de productos con IA
@login_required
@require_http_methods(["POST"])
def comparar_productos_ia(request):
    """
    Compara dos productos usando IA
    """
    try:
        data = json.loads(request.body)
        producto1_id = data.get('producto1_id')
        producto2_id = data.get('producto2_id')
        
        if not producto1_id or not producto2_id:
            return JsonResponse({
                "success": False,
                "error": "Se requieren dos productos para comparar"
            }, status=400)
        
        # Obtener productos
        try:
            p1 = Product.objects.get(id=producto1_id)
            p2 = Product.objects.get(id=producto2_id)
        except Product.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Uno o ambos productos no existen"
            }, status=404)
        
        # Preparar datos con calificaciones
        from django.db.models import Avg, Count
        
        p1_reviews = p1.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        p2_reviews = p2.reviews.aggregate(avg=Avg('rating'), count=Count('id'))
        
        producto1_data = {
            'name': p1.name,
            'brand': p1.brand,
            'price': float(p1.price),
            'type': p1.type,
            'description': p1.description,
            'warranty': p1.warranty,
            'avg_rating': round(p1_reviews['avg'], 2) if p1_reviews['avg'] else 0,
            'reviews_count': p1_reviews['count']
        }
        
        producto2_data = {
            'name': p2.name,
            'brand': p2.brand,
            'price': float(p2.price),
            'type': p2.type,
            'description': p2.description,
            'warranty': p2.warranty,
            'avg_rating': round(p2_reviews['avg'], 2) if p2_reviews['avg'] else 0,
            'reviews_count': p2_reviews['count']
        }
        
        gemini_service = GeminiService()
        resultado = gemini_service.comparar_productos(producto1_data, producto2_data)
        
        # Agregar información básica de productos
        if resultado['success']:
            resultado['productos'] = {
                'producto1': {
                    'id': p1.id,
                    'name': p1.name,
                    'price': float(p1.price),
                    'image': p1.image.url if p1.image else None
                },
                'producto2': {
                    'id': p2.id,
                    'name': p2.name,
                    'price': float(p2.price),
                    'image': p2.image.url if p2.image else None
                }
            }
        
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)

class CompararProductosView(TemplateView):
    template_name = "pages/comparar_productos.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(quantity__gt=0).order_by('name')
        # Pre-seleccionar producto si viene en query params
        context['preselected_product1'] = self.request.GET.get('producto1', '')
        context['preselected_product2'] = self.request.GET.get('producto2', '')
        
        return context
