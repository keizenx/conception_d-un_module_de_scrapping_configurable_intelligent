# backend/api/admin.py
# Configuration de l'interface d'administration Django
# Enregistre les modèles pour les gérer via l'admin
# RELEVANT FILES: api/models.py, config/urls.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, ScrapingSession, ScrapedData, Report,
    AnalysisResult, SubdomainDiscovery, PathDiscovery, 
    PageImage, ContentType, ApiKey, Webhook
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin pour le modèle User étendu."""
    list_display = ['username', 'email', 'first_name', 'last_name', 'company', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'company']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('phone', 'company')}),
    )


@admin.register(ScrapingSession)
class ScrapingSessionAdmin(admin.ModelAdmin):
    """Admin pour ScrapingSession."""
    list_display = ['id', 'user', 'url_short', 'status', 'started_at', 'completed_at', 'total_items']
    list_filter = ['status', 'started_at']
    search_fields = ['url', 'user__username']
    readonly_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']
    
    def url_short(self, obj):
        """Affiche une version courte de l'URL."""
        return obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
    url_short.short_description = 'URL'


@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    """Admin pour ScrapedData."""
    list_display = ['id', 'session_id', 'element_type', 'extracted_at']
    list_filter = ['element_type', 'extracted_at']
    search_fields = ['session__url', 'element_type']
    readonly_fields = ['extracted_at']
    ordering = ['-extracted_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin pour Report."""
    list_display = ['id', 'title', 'user', 'format', 'created_at']
    list_filter = ['format', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    """Admin pour AnalysisResult."""
    list_display = ['id', 'domain', 'user', 'is_accessible', 'total_pages', 'total_subdomains', 'analyzed_at']
    list_filter = ['is_accessible', 'include_subdomains', 'analyzed_at']
    search_fields = ['domain', 'url', 'user__username']
    readonly_fields = ['analyzed_at', 'analysis_duration']
    ordering = ['-analyzed_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'url', 'domain')
        }),
        ('Résultats', {
            'fields': ('is_accessible', 'status_code', 'protection_detected', 'tech_stack')
        }),
        ('Statistiques', {
            'fields': ('total_pages', 'total_subdomains', 'total_paths', 'content_types_count')
        }),
        ('Configuration', {
            'fields': ('include_subdomains',)
        }),
        ('Métadonnées', {
            'fields': ('analyzed_at', 'analysis_duration')
        }),
    )


@admin.register(SubdomainDiscovery)
class SubdomainDiscoveryAdmin(admin.ModelAdmin):
    """Admin pour SubdomainDiscovery."""
    list_display = ['subdomain', 'analysis', 'is_scrapable', 'status_code', 'source', 'discovered_at']
    list_filter = ['is_scrapable', 'source', 'discovered_at']
    search_fields = ['subdomain', 'analysis__domain']
    readonly_fields = ['discovered_at']
    ordering = ['subdomain']


@admin.register(PathDiscovery)
class PathDiscoveryAdmin(admin.ModelAdmin):
    """Admin pour PathDiscovery."""
    list_display = ['path', 'title', 'is_main_page', 'total_links', 'total_images', 'discovered_at']
    list_filter = ['is_main_page', 'discovered_at']
    search_fields = ['path', 'title', 'url']
    readonly_fields = ['discovered_at']
    ordering = ['path']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('analysis', 'path', 'url', 'title', 'is_main_page')
        }),
        ('Preview', {
            'fields': ('meta_description', 'text_preview')
        }),
        ('Statistiques', {
            'fields': ('total_links', 'total_images', 'total_forms')
        }),
        ('Métadonnées', {
            'fields': ('discovered_at',)
        }),
    )


@admin.register(PageImage)
class PageImageAdmin(admin.ModelAdmin):
    """Admin pour PageImage."""
    list_display = ['alt', 'src_short', 'width', 'height']
    search_fields = ['alt', 'src']
    
    def src_short(self, obj):
        return obj.src[:60] + '...' if len(obj.src) > 60 else obj.src
    src_short.short_description = 'Source'


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    """Admin pour ContentType."""
    list_display = ['title', 'type_id', 'count', 'icon', 'analysis']
    list_filter = ['type_id']
    search_fields = ['title', 'type_id', 'description']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('analysis', 'type_id', 'title', 'description', 'icon')
        }),
        ('Détection', {
            'fields': ('count', 'selector', 'detected_fields')
        }),
        ('Aperçu', {
            'fields': ('preview_items',)
        }),
    )


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    """Admin pour ApiKey."""
    list_display = ['name', 'user', 'key_prefix', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username', 'key_prefix']
    readonly_fields = ['key', 'key_prefix', 'created_at', 'last_used']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'name', 'is_active')
        }),
        ('Clé', {
            'fields': ('key', 'key_prefix'),
            'description': 'La clé complète est affichée ici mais ne sera jamais affichée à nouveau.'
        }),
        ('Utilisation', {
            'fields': ('created_at', 'last_used')
        }),
    )


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin pour Webhook."""
    list_display = ['url_short', 'user', 'is_active', 'events_count', 'success_count', 'failure_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['url', 'user__username']
    readonly_fields = ['created_at', 'last_triggered', 'success_count', 'failure_count']
    ordering = ['-created_at']
    
    def url_short(self, obj):
        return obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
    url_short.short_description = 'URL'
    
    def events_count(self, obj):
        return len(obj.events)
    events_count.short_description = 'Événements'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'url', 'is_active')
        }),
        ('Configuration', {
            'fields': ('events',)
        }),
        ('Statistiques', {
            'fields': ('created_at', 'last_triggered', 'success_count', 'failure_count')
        }),
    )
