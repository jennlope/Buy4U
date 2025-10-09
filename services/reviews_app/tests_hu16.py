from django.test import TestCase
from shop.models import Product
from django.contrib.auth import get_user_model
from services.reviews_app.models import Review

class HU16RatingStatsTests(TestCase):
    def setUp(self):
        self.u = get_user_model().objects.create_user(username="u1", password="p")
        self.p1 = Product.objects.create(name="P1", price=10, brand="B", quantity=1, type="T")
        self.p2 = Product.objects.create(name="P2", price=5, brand="B", quantity=1, type="T")
        Review.objects.create(product=self.p1, user=self.u, text="a", rating=5)
        Review.objects.create(product=self.p1, user=self.u, text="b", rating=3)
        Review.objects.create(product=self.p2, user=self.u, text="c", rating=4)

    def test_rating_stats_json(self):
        self.client.login(username="u1", password="p")
        # user is not staff -> should be redirected/forbidden
        resp = self.client.get("/admin/reports/ratings/data/")
        self.assertIn(resp.status_code, (302, 403))

        # make user staff
        self.u.is_staff = True
        self.u.save()
        resp = self.client.get("/admin/reports/ratings/data/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # find p1 stats
        p1 = [x for x in data["rating_stats"] if x["id"] == self.p1.id][0]
        self.assertEqual(p1["reviews_count"], 2)
        self.assertAlmostEqual(p1["avg_rating"], 4.0, places=2)
