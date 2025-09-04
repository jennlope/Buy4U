from django.test import TestCase, Client
from .models import BrowsingHistory

class BrowsingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_logs_product_view(self):
        self.client.get('/shop/product/2/')
        self.assertTrue(BrowsingHistory.objects.filter(action='product_view').exists())

    def test_logs_search_query(self):
        # Tu URL real de filtro/búsqueda:
        self.client.get('/shop/?name=smart&min_price=&max_price=&brand=&type=')
        # Debe registrar al menos 'name=smart' en query (los vacíos se omiten)
        self.assertTrue(
            BrowsingHistory.objects.filter(action='search', query__icontains='name=smart').exists()
        )
