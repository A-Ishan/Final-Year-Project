from django.contrib import admin
from django.urls import path
from authentication import views

urlpatterns = [  # Corrected from `urlspatterns` to `urlpatterns`
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
]
