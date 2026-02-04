# backend/api/urls.py
# Routes API pour l'application SCRAPER PRO
# Définit tous les endpoints REST accessibles depuis le frontend
# RELEVANT FILES: api/views.py, config/urls.py, api/serializers.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from .views import (
    AuthViewSet,
    DashboardViewSet,
    AnalysisViewSet,
    ScrapingViewSet,
    ResultsViewSet,
    ReportsViewSet,
    SettingsViewSet,
    export_results
)

# Router DRF pour les ViewSets
router = DefaultRouter()
router.register(r'scraping', ScrapingViewSet, basename='scraping')
router.register(r'results', ResultsViewSet, basename='results')
router.register(r'reports', ReportsViewSet, basename='reports')

urlpatterns = [
    # Routes d'authentification
    path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='auth-register'),
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('auth/me/', AuthViewSet.as_view({'get': 'me'}), name='auth-me'),
    path('auth/profile/', AuthViewSet.as_view({'get': 'profile', 'put': 'profile'}), name='auth-profile'),
    path('auth/change-password/', AuthViewSet.as_view({'post': 'change_password'}), name='auth-change-password'),
    path('auth/delete-account/', AuthViewSet.as_view({'delete': 'delete_account'}), name='auth-delete-account'),
    path('auth/upload-avatar/', AuthViewSet.as_view({'post': 'upload_avatar'}), name='auth-upload-avatar'),
    path('auth/delete-avatar/', AuthViewSet.as_view({'delete': 'delete_avatar'}), name='auth-delete-avatar'),
    
    # Routes du dashboard
    path('dashboard/stats/', DashboardViewSet.as_view({'get': 'stats'}), name='dashboard-stats'),
    path('dashboard/recent_sessions/', DashboardViewSet.as_view({'get': 'recent_sessions'}), name='dashboard-recent-sessions'),
    path('dashboard/activity/', DashboardViewSet.as_view({'get': 'activity'}), name='dashboard-activity'),
    
    # Routes d'analyse
    path('analysis/quick_analyze/', AnalysisViewSet.as_view(
        {'post': 'quick_analyze'}, 
        permission_classes=[AllowAny]
    ), name='analysis-quick-analyze'),
    path('analysis/analyze/', AnalysisViewSet.as_view({'post': 'analyze'}), name='analysis-analyze'),
    
    # Routes d'export - AVANT le router pour éviter les conflits
    path('export/<int:session_id>/', export_results, name='export-results'),
    
    # Routes des paramètres
    path('settings/api-keys/', SettingsViewSet.as_view({'get': 'api_keys', 'post': 'api_keys'}), name='settings-api-keys'),
    path('settings/api-keys/<int:key_id>/', SettingsViewSet.as_view({'delete': 'delete_api_key'}), name='settings-delete-api-key'),
    path('settings/webhooks/', SettingsViewSet.as_view({'get': 'webhooks', 'post': 'webhooks'}), name='settings-webhooks'),
    path('settings/webhooks/<int:webhook_id>/', SettingsViewSet.as_view({'delete': 'delete_webhook'}), name='settings-delete-webhook'),
    
    # Routes du router (scraping, results, reports) - Le router gère /results/{id}/export/ via l'action export
    path('', include(router.urls)),
]
