from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import Event

User = get_user_model()


class TrackingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client.login(username="tester", password="pass1234")

    def test_logs_product_view(self):
        resp = self.client.get("/shop/product/1/")
        # El test asume que la URL existe; si no, crea una vista dummy o ajusta la ruta.
        self.assertTrue(Event.objects.filter(event_type="view").exists())

    def test_logs_click(self):
        self.client.get("/shop/product/1/?clicked=1")
        self.assertTrue(Event.objects.filter(event_type="click").exists())
