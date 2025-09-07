from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from shop.models import Product
from services.reviews_app.models import Review

User = get_user_model()

class HU09ReviewCountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Producto C",
            price=50,
            brand="Marca",
            warranty="6 meses",
            description="Desc",
            quantity=5,
            type="General",
        )
        u1 = User.objects.create_user(username="u1", password="Pas788888*s")
        u2 = User.objects.create_user(username="u2", password="Pas788888*s")
        Review.objects.create(product=self.product, user=u1, text="okgggggggggggg", rating=4)
        Review.objects.create(product=self.product, user=u2, text="biennnnnnnnnnnnnnnnnnnn", rating=5)

    def test_review_count_is_shown_and_exact(self):
        url = reverse("product_detail", args=[self.product.id])
        resp = self.client.get(url)
        # Debe mostrar "(2 reseñas)"
        self.assertContains(resp, "(2 reseñas)")

        # Agregamos otra reseña y debe reflejar "(3 reseñas)"
        u3 = User.objects.create_user(username="u3", password="pass")
        Review.objects.create(product=self.product, user=u3, text="Suaveeeeeeeee", rating=3)

        resp = self.client.get(url)
        self.assertContains(resp, "(3 reseñas)")
