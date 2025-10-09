from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from services.browsing_app.models import BrowsingHistory
from shop.models import Product
from orders.models import Order, ProductOrder
from services.reviews_app.models import Review
from datetime import datetime, timedelta, date

class ReportsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user("admin", "a@a.com", "pass", is_staff=True)
        self.client = Client()
        self.client.login(username="admin", password="pass")
        # create sample product and data
        self.p = Product.objects.create(name="P1", price=10.0, brand="B")
        BrowsingHistory.objects.create(action="product_view", product_id=self.p.id, session_key="s1", created_at=datetime.now())
        # create order (adjust to your models)
        o = Order.objects.create(user=self.admin, created_at=datetime.now())
        ProductOrder.objects.create(order=o, product=self.p, quantity=2)
        Review.objects.create(product=self.p, user=self.admin, rating=5, text="great")

    def test_reports_overview_accessible(self):
        r = self.client.get(reverse("admin_reports_overview"))
        self.assertEqual(r.status_code, 200)

    def test_reports_data_json(self):
        r = self.client.get(reverse("admin_reports_data_json"))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("labels", data)
        self.assertIn("visits", data)
        self.assertIn("purchases", data)
