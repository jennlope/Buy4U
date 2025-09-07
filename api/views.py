from django.shortcuts import render
from rest_framework import generics, permissions

from shop.models import Product

from .serializers import ProductSerializer


# Create your views here.
class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(quantity__gt=0)  # Solo productos en stock
    permission_classes = [
        permissions.AllowAny
    ]  # Permite el acceso a todos los usuarios sin autenticación


class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()  # Obtiene todos los productos
    permission_classes = [
        permissions.AllowAny
    ]  # Permite el acceso a todos los usuarios sin autenticación
