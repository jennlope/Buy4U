from django.urls import path
from .views import loginView, logoutView, registerView

urlpatterns = [
    path('login/', loginView.as_view(), name='login'),
    path('logout/', logoutView.as_view(), name='logout'),
    path('register/', registerView.as_view(), name='register'),
]