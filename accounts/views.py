from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView

# Create your views here.
class loginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('home')  # Redirige al home si el login fue exitoso

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Login - Online Store',
            'subtitle': 'Login to your account',
        })
        return context

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Username OR password is incorrect')
            return self.form_invalid(form)
    
class logoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class registerView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redirige al login si el registro fue exitoso

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Register - Online Store',
            'subtitle': 'Sign up',
        })
        return context

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f'Account was created for {user.username}')
        return super().form_valid(form)