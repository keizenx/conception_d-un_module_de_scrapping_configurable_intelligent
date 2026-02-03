# backend/config/urls.py
# Routes principales du projet Django SCRAPER PRO
# Inclut les routes de l'admin et de l'API
# RELEVANT FILES: api/urls.py, api/views.py, config/settings.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include('api.urls')),
]
