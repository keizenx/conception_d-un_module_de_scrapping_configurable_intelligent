# backend/config/urls.py
# Routes principales du projet Django SCRAPER PRO
# Inclut les routes de l'admin et de l'API
# RELEVANT FILES: api/urls.py, api/views.py, config/settings.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include('api.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
