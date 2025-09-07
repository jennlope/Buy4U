"""
URL configuration for Buy4U_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import set_language
from django.views.decorators.csrf import csrf_exempt
from shop.views import GenerarReporteView 

urlpatterns = [
    path('admin/generar_reporte/<str:tipo>/', GenerarReporteView.as_view(), name='generar_reporte'),
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('set_language/', csrf_exempt(set_language), name='set_language'),
    path('api/', include('api.urls')),
    path('', include('services.reviews_app.urls')),  
    
    path('admin/', admin.site.urls),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)