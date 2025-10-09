from django.test import Client, TestCase
from .models import BrowsingHistory
from django.contrib.auth import get_user_model
from shop.models import Product
from django.urls import reverse
from datetime import datetime, timedelta

class BrowsingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_logs_product_view(self):
        self.client.get("/shop/product/2/")
        self.assertTrue(BrowsingHistory.objects.filter(action="product_view").exists())

    def test_logs_search_query(self):
        # Tu URL real de filtro/búsqueda:
        self.client.get("/shop/?name=smart&min_price=&max_price=&brand=&type=")
        # Debe registrar al menos 'name=smart' en query (los vacíos se omiten)
        self.assertTrue(
            BrowsingHistory.objects.filter(
                action="search", query__icontains="name=smart"
            ).exists()
        )

    def test_search_history_saved_for_authenticated_user(self):
        user = get_user_model().objects.create_user('u','u@example.com','pwd')
        c = Client()
        c.force_login(user)
        resp = c.get('/shop/?name=smart')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(BrowsingHistory.objects.filter(user=user, action='search', query__icontains='smart').exists())



User = get_user_model()

class AdminInlineBrowsingTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin','a@a.com','pwd', is_staff=True)
        self.user = User.objects.create_user('u','u@u.com','pwd')
        p = Product.objects.create(name='X', price=1)
        BrowsingHistory.objects.create(user=self.user, action='search', query='phone', product_id=p.id, path='/shop/?q=phone')
        self.client = Client()
        self.client.force_login(self.admin)

    def test_manage_page_contains_browsing_history(self):
        resp = self.client.get('/admin_dashboard')  # o la URL que uses para admin_product_view
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Historial de búsqueda')
        self.assertContains(resp, 'phone')

class AnalyticsFilterTests(TestCase):
    def setUp(self):
        # usuarios
        self.staff = User.objects.create_user("admin", "admin@example.com", "pass")
        self.staff.is_staff = True
        self.staff.save()

        self.u1 = User.objects.create_user("u1", "u1@example.com", "pass")
        self.u2 = User.objects.create_user("u2", "u2@example.com", "pass")

        # productos (with types)
        self.p1 = Product.objects.create(name="P1", price=10, brand="B", warranty="", description="", quantity=1, type="Electronics")
        self.p2 = Product.objects.create(name="P2", price=20, brand="B", warranty="", description="", quantity=1, type="Home")

        # browsing records: u1 search and view p1
        now = datetime.now()
        BrowsingHistory.objects.create(user=self.u1, session_key="s1", action="search", query="smart", path="/shop/?name=smart", created_at=now - timedelta(days=1))
        BrowsingHistory.objects.create(user=self.u1, session_key="s1", action="product_view", product_id=self.p1.id, path=f"/shop/product/{self.p1.id}/", created_at=now)

        # u2 views p2 today
        BrowsingHistory.objects.create(user=self.u2, session_key="s2", action="product_view", product_id=self.p2.id, path=f"/shop/product/{self.p2.id}/", created_at=now)

        self.client = Client()

    def test_admin_manage_page_get(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("admin_dashboard"))  # ajusta la url name si es otra
        self.assertEqual(resp.status_code, 200)

    def test_filter_by_category(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("admin_dashboard"), {"bh_category": "Electronics"})
        self.assertContains(resp, "P1")  # el template muestra product_id o nombre relativo