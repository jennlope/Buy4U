from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from shop.models import Product
from unittest.mock import patch, MagicMock
import json

User = get_user_model()

class IAFeaturesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user('admin', 'a@a.com', 'pass', is_staff=True)
        self.user = User.objects.create_user('user', 'u@u.com', 'pass')
        
        self.p1 = Product.objects.create(
            name='iPhone 14 Pro Max',
            brand='Apple',
            price=1099,
            type='Smartphone',
            quantity=5,
            description='Latest iPhone'
        )
        
        self.p2 = Product.objects.create(
            name='Samsung Galaxy S23',
            brand='Samsung',
            price=999,
            type='Smartphone',
            quantity=5,
            description='Latest Samsung'
        )
    
    @patch('shop.ai_service.genai.GenerativeModel')
    def test_recomendar_precio_admin_only(self, mock_model):
        """Solo admin puede acceder a recomendación de precios"""
        url = '/api/ia/recomendar-precio/'
        data = {'nombre': 'iPhone 14', 'marca': 'Apple', 'tipo': 'Smartphone'}
        
        # Sin login -> 302 redirect
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        
        # Usuario normal -> 302 redirect
        self.client.login(username='user', password='pass')
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        
        # Admin -> 200 OK
        self.client.login(username='admin', password='pass')
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = '{"precio_recomendado": 999, "precio_minimo": 899, "precio_maximo": 1099, "justificacion": "test", "confianza": "alta"}'
        mock_model.return_value = mock_instance
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_comparar_productos_requires_login(self):
        """Comparar productos requiere login"""
        url = '/api/ia/comparar-productos/'
        data = {'producto1_id': self.p1.id, 'producto2_id': self.p2.id}
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 302)
    
    @patch('shop.ai_service.genai.GenerativeModel')
    def test_comparar_productos_success(self, mock_model):
        """Comparación exitosa de productos"""
        self.client.login(username='user', password='pass')
        
        mock_instance = MagicMock()
        mock_response = '''
        {
            "resumen": "Test comparison",
            "ventajas_producto1": ["Better camera"],
            "ventajas_producto2": ["Lower price"],
            "mejor_relacion_calidad_precio": "producto2",
            "recomendacion": "Test recommendation",
            "diferencia_precio": 100,
            "veredicto": "Both are good"
        }
        '''
        mock_instance.generate_content.return_value.text = mock_response
        mock_model.return_value = mock_instance
        
        url = '/api/ia/comparar-productos/'
        data = {'producto1_id': self.p1.id, 'producto2_id': self.p2.id}
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.content)
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('productos', result)
    
    def test_comparar_productos_invalid_ids(self):
        """Error cuando los IDs son inválidos"""
        self.client.login(username='user', password='pass')
        
        url = '/api/ia/comparar-productos/'
        data = {'producto1_id': 9999, 'producto2_id': 9998}
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        
        result = json.loads(response.content)
        self.assertFalse(result['success'])