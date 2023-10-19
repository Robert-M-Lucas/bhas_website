from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.login),
    path('logout/', views.logout),
    path('logout/instant/', views.instant_logout),
    path('', views.auth),
]
