from django.test import Client, TestCase
from .models import BrowsingHistory
from django.contrib.auth import get_user_model
from shop.models import Product


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
