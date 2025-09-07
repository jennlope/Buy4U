from django.utils.deprecation import MiddlewareMixin

from .models import BrowsingHistory


class BrowsingHistoryMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Asegurar sesión
        if not request.session.session_key:
            request.session.save()

        path = request.path
        session_key = request.session.session_key

        # 1) Visitas a producto
        if path.startswith("/shop"):
            product_id = (
                request.GET.get("product_id")
                or view_kwargs.get("pk")
                or view_kwargs.get("id")
            )
            # Registra vistas de producto (cuando aplica)
            if "/shop/product/" in path:
                BrowsingHistory.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=session_key,
                    action="product_view",
                    product_id=product_id if product_id else None,
                    path=path,
                )

        # 2) Búsquedas / filtros (por querystring)
        # Considera estos parámetros como "de búsqueda":
        search_keys = {
            "q",
            "query",
            "name",
            "brand",
            "type",
            "min_price",
            "max_price",
            "category",
        }
        querydict = request.GET

        # Extrae pares (k, v) no vacíos de las keys de búsqueda
        non_empty_pairs = [
            (k, v) for k, v in querydict.items() if k in search_keys and v
        ]
        if path.startswith("/shop") and non_empty_pairs:
            # Normaliza la query para guardarla (solo pares con valor)
            normalized_query = "&".join(f"{k}={v}" for k, v in non_empty_pairs)
            BrowsingHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                action="search",
                query=normalized_query[:255],  # cabe en CharField(255)
                path=path,
            )
        return None
