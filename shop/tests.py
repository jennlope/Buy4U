from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from shop.models import Product


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="test1234")

    def test_login_valido(self):
        response = self.client.post(
            reverse("login"), {"username": "tester", "password": "test1234"}
        )
        self.assertEqual(response.status_code, 302)  # Redirige tras login
        self.assertRedirects(response, reverse("home"))

    def test_login_invalido(self):
        response = self.client.post(
            reverse("login"), {"username": "tester", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "<ul", html=False
        )  # Se muestra la lista de errores


class RegistroTests(TestCase):
    def test_registro_valido(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "nuevo_user",
                "password1": "pass123456",
                "password2": "pass123456",
                "email": "nuevo@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nuevo_user").exists())

    def test_registro_contraseñas_diferentes(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "fallo_user",
                "password1": "abc123",
                "password2": "xyz789",
                "email": "fallo@example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The two password fields didn’t match.")


class CatalogoTests(TestCase):
    def setUp(self):
        image = SimpleUploadedFile(
            "test.jpg", b"file_content", content_type="image/jpeg"
        )
        Product.objects.create(
            name="Prueba",
            price=1000,
            brand="TestBrand",
            description="Desc",
            quantity=5,
            warranty="6 meses",
            type="Electrónica",
            image=image,
        )
