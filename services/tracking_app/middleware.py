from django.utils.deprecation import MiddlewareMixin

from .models import Event


class UserInteractionMiddleware(MiddlewareMixin):
    """
    Registra vistas y clics:
    - Cualquier path que empiece por /shop se considera vista de producto.
    - Si llega ?clicked=1, registra un clic.
    Ajusta los prefijos a tus URLs reales si no usas /shop.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Asegurar session para usuarios anónimos
        if not request.session.session_key:
            request.session.save()

        path = request.path
        product_id = (
            request.GET.get("product_id")
            or view_kwargs.get("pk")
            or view_kwargs.get("id")
        )
        session_key = request.session.session_key

        if path.startswith("/shop"):
            Event.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                event_type="view",
                product_id=product_id if product_id else None,
                path=path,
                metadata={"method": request.method},
            )

        if request.GET.get("clicked") == "1":
            Event.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                event_type="click",
                product_id=product_id if product_id else None,
                path=path,
                metadata={"method": request.method},
            )
        return None
