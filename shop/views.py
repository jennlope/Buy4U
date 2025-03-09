from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect 
from django.views.generic import TemplateView, ListView
from django.views import View
from django import forms

# Create your views here.
class HomePageView(TemplateView):
    template_name = 'pages/home.html'