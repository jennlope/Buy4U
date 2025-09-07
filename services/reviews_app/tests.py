from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from shop.models import Product
from orders.models import Order, ProductOrder
from .models import Review

User = get_user_model()

class ReviewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='u1', password='pass1234')
        self.p = Product.objects.create(name='Prod X', price=100)
        # Orden del usuario con el producto
        self.order = Order.objects.create(user=self.user, status='delivered')
        ProductOrder.objects.create(order=self.order, product=self.p, quantity=1)

    def test_only_buyer_can_see_form_and_post(self):
        # sin login -> redirige
        resp = self.client.post(reverse('product_review', kwargs={'id': self.p.id}), {'text':'Excelente!'})
        self.assertEqual(resp.status_code, 302)

        # login
        self.client.login(username='u1', password='pass1234')
        # puede reseñar
        resp = self.client.post(reverse('product_review', kwargs={'id': self.p.id}), {'text':'Excelente producto!!'})
        self.assertEqual(Review.objects.filter(product=self.p, user=self.user).count(), 1)

    def test_user_cannot_review_twice(self):
        self.client.login(username='u1', password='pass1234')
        # 1ra reseña (válida: >=10 chars)
        self.client.post(
            reverse('product_review', kwargs={'id': self.p.id}),
            {'text': 'Muy bueno!!!'},  # 12 chars
            follow=True
        )
        # 2da reseña (debe ignorarse)
        self.client.post(
            reverse('product_review', kwargs={'id': self.p.id}),
            {'text': 'Repetida otra vez!'},
            follow=True
        )
        self.assertEqual(
            Review.objects.filter(product=self.p, user=self.user).count(), 1
        )
