from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from shop.models import Product
from io import BytesIO

class ShopViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")

        # Imagen dummy
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

        # Crear productos de prueba
        self.product1 = Product.objects.create(
            name="Laptop Gamer", price=5000000, stock=10, image=image
        )
        self.product2 = Product.objects.create(
            name="Mouse", price=80000, stock=20, image=image
        )

    def test_shop_view_loads(self):
        """La vista principal de la tienda carga correctamente"""
        url = reverse("shop")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/shop.html")
        self.assertContains(response, "Laptop Gamer")
        self.assertContains(response, "Mouse")

    def test_shop_view_price_filter(self):
        """Filtrar productos por rango de precio"""
        url = reverse("shop") + "?min_price=100000&max_price=1000000"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Debe mostrar el mouse pero no la laptop
        self.assertContains(response, "Mouse")
        self.assertNotContains(response, "Laptop Gamer")

    def test_product_detail_view(self):
        """La vista de detalle del producto carga correctamente"""
        url = reverse("product_detail", args=[self.product1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/product_detail.html")
        self.assertContains(response, "Laptop Gamer")

    def test_add_product_to_cart(self):
        """Agregar un producto al carrito"""
        url = reverse("add_cart", args=[self.product1.id])
        self.client.get(url)
        session = self.client.session
        cart = session.get("cart", {})
        self.assertIn(str(self.product1.id), cart)

    def test_update_cart_quantity(self):
        """Actualizar cantidad de producto en el carrito"""
        self.client.get(reverse("add_cart", args=[self.product2.id]))
        url = reverse("cart_update_quantity", args=[self.product2.id])
        self.client.post(url, {"quantity": 3})
        session = self.client.session
        cart = session.get("cart", {})
        self.assertEqual(cart[str(self.product2.id)]["quantity"], 3)

    def test_remove_product_from_cart(self):
        """Eliminar un producto del carrito"""
        self.client.get(reverse("add_cart", args=[self.product1.id]))
        url = reverse("remove_cart", args=[self.product1.id])
        self.client.get(url)
        session = self.client.session
        cart = session.get("cart", {})
        self.assertNotIn(str(self.product1.id), cart)

    def test_admin_dashboard_requires_login(self):
        """El panel de administración redirige si el usuario no está autenticado"""
        url = reverse("admin_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirige al login

    def test_admin_dashboard_loads_for_staff(self):
        """El panel de administración carga correctamente para usuario staff"""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="testuser", password="12345")
        url = reverse("admin_dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/product_dashboard.html")