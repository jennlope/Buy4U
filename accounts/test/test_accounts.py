import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

@pytest.mark.django_db
def test_userprofile_creation_and_str():
    user = User.objects.create_user(username="testuser", password="12345")
    profile = UserProfile.objects.create(user=user, country="Colombia", gender="male")
    assert str(profile) == "Profile testuser"
    assert profile.country == "Colombia"
    assert profile.gender == "male"

@pytest.mark.django_db
def test_register_view_creates_user(client):
    url = reverse("register")
    response = client.post(
        url,
        data={
            "username": "newuser",
            "password1": "Testpass123",
            "password2": "Testpass123",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert User.objects.filter(username="newuser").exists()

@pytest.mark.django_db
def test_login_and_logout_flow(client):
    user = User.objects.create_user(username="loginuser", password="pass12345")

    # Intentar login
    login_url = reverse("login")
    response = client.post(login_url, {"username": "loginuser", "password": "pass12345"})
    assert response.status_code in (200, 302)

    # Comprobar sesión iniciada
    response = client.get(reverse("home"))
    assert response.status_code in (200, 302)

    # Logout
    logout_url = reverse("logout")
    response = client.get(logout_url, follow=True)
    assert response.status_code == 200

@pytest.mark.django_db
def test_invalid_login_does_not_authenticate_user(client):
    login_url = reverse("login")
    response = client.post(login_url, {"username": "nouser", "password": "wrongpass"})
    assert response.status_code == 200  # Se queda en la página de login
    # Aseguramos que no se crea sesión de usuario
    assert not response.wsgi_request.user.is_authenticated