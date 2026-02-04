# backend/api/models.py
# Modèles de données pour l'application SCRAPER PRO
# Définit User, ScrapingSession, ScrapedData et Report
# RELEVANT FILES: api/serializers.py, api/views.py, config/settings.py, api/admin.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import json


class User(AbstractUser):
    """
    Modèle utilisateur étendu pour SCRAPER PRO.
    Hérite de AbstractUser pour avoir tous les champs standard (username, email, password, etc.)
    """
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return self.username


class ScrapingSession(models.Model):
    """
    Session de scraping : représente une tentative d'extraction de données depuis une URL.
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scraping_sessions')
    url = models.URLField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Configuration du scraping (stockée en JSON)
    configuration = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Logs de progression
    progress_logs = models.JSONField(default=list, blank=True)
    current_step = models.CharField(max_length=200, blank=True, null=True)
    
    # Statistiques
    total_items = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'scraping_sessions'
        verbose_name = 'Session de scraping'
        verbose_name_plural = 'Sessions de scraping'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.url[:50]} ({self.status})"
    
    def mark_completed(self):
        """Marque la session comme terminée."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Marque la session comme échouée avec un message d'erreur."""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()
    
    def add_log(self, message, log_type='info'):
        """Ajoute un message de log à la session."""
        if not isinstance(self.progress_logs, list):
            self.progress_logs = []
        
        self.progress_logs.append({
            'timestamp': timezone.now().isoformat(),
            'message': message,
            'type': log_type
        })
        self.current_step = message
        self.save(update_fields=['progress_logs', 'current_step'])


class ScrapedData(models.Model):
    """
    Données extraites lors d'une session de scraping.
    Chaque entrée représente un élément extrait (produit, article, etc.)
    """
    session = models.ForeignKey(ScrapingSession, on_delete=models.CASCADE, related_name='scraped_data')
    
    # Données extraites (stockées en JSON)
    data = models.JSONField(default=dict)
    
    # Métadonnées
    extracted_at = models.DateTimeField(auto_now_add=True)
    element_type = models.CharField(max_length=100, blank=True, null=True)  # product, article, etc.
    source_url = models.URLField(max_length=2000, blank=True, null=True)
    
    class Meta:
        db_table = 'scraped_data'
        verbose_name = 'Donnée extraite'
        verbose_name_plural = 'Données extraites'
        ordering = ['-extracted_at']
    
    def __str__(self):
        return f"Data from {self.session.url[:30]} at {self.extracted_at}"


class Report(models.Model):
    """
    Rapport généré à partir d'une session de scraping.
    Peut être exporté en PDF, CSV, Excel, etc.
    """
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]
    
    session = models.ForeignKey(ScrapingSession, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    
    title = models.CharField(max_length=200)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='pdf')
    
    # Contenu du rapport
    content = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        verbose_name = 'Rapport'
        verbose_name_plural = 'Rapports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.format}) - {self.created_at}"


class AnalysisResult(models.Model):
    """
    Résultat d'analyse d'un site web.
    Stocke les informations de base du site analysé.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    url = models.URLField(max_length=2000)
    domain = models.CharField(max_length=255)
    
    # Résultats de base
    is_accessible = models.BooleanField(default=True)
    status_code = models.IntegerField(null=True, blank=True)
    protection_detected = models.CharField(max_length=100, blank=True, null=True)
    tech_stack = models.JSONField(default=list, blank=True)
    
    # Statistiques
    total_pages = models.IntegerField(default=0)
    total_subdomains = models.IntegerField(default=0)
    total_paths = models.IntegerField(default=0)
    content_types_count = models.IntegerField(default=0)
    
    # Configuration utilisée
    include_subdomains = models.BooleanField(default=False)
    
    # Métadonnées
    analyzed_at = models.DateTimeField(auto_now_add=True)
    analysis_duration = models.FloatField(null=True, blank=True)  # en secondes
    
    class Meta:
        db_table = 'analysis_results'
        verbose_name = 'Résultat d\'analyse'
        verbose_name_plural = 'Résultats d\'analyse'
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return f"{self.domain} - {self.analyzed_at.strftime('%Y-%m-%d %H:%M')}"


class SubdomainDiscovery(models.Model):
    """
    Sous-domaines découverts lors d'une analyse.
    """
    analysis = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='subdomains')
    subdomain = models.CharField(max_length=255)
    
    # Statut de scraping
    is_scrapable = models.BooleanField(default=True)
    status_code = models.IntegerField(null=True, blank=True)
    protection = models.CharField(max_length=100, blank=True, null=True)
    
    # Source de découverte
    source = models.CharField(max_length=50)  # crt.sh, hackertarget, etc.
    
    # Métadonnées
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subdomain_discoveries'
        verbose_name = 'Sous-domaine découvert'
        verbose_name_plural = 'Sous-domaines découverts'
        ordering = ['subdomain']
    
    def __str__(self):
        return f"{self.subdomain} ({self.source})"


class PathDiscovery(models.Model):
    """
    Chemins/pages découverts lors d'une analyse.
    """
    analysis = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='paths')
    path = models.CharField(max_length=500)
    url = models.URLField(max_length=2000)
    
    # Informations sur la page
    title = models.CharField(max_length=500, blank=True, null=True)
    is_main_page = models.BooleanField(default=False)  # Page de navigation principale
    
    # Preview de la page
    meta_description = models.TextField(blank=True, null=True)
    text_preview = models.TextField(blank=True, null=True)
    
    # Statistiques de la page
    total_links = models.IntegerField(default=0)
    total_images = models.IntegerField(default=0)
    total_forms = models.IntegerField(default=0)
    
    # Métadonnées
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'path_discoveries'
        verbose_name = 'Chemin découvert'
        verbose_name_plural = 'Chemins découverts'
        ordering = ['path']
    
    def __str__(self):
        return f"{self.path} - {self.title or 'Sans titre'}"


class PageImage(models.Model):
    """
    Images découvertes sur une page.
    """
    path = models.ForeignKey(PathDiscovery, on_delete=models.CASCADE, related_name='images')
    src = models.URLField(max_length=2000)
    alt = models.CharField(max_length=500, blank=True, null=True)
    width = models.CharField(max_length=20, blank=True, null=True)
    height = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = 'page_images'
        verbose_name = 'Image de page'
        verbose_name_plural = 'Images de page'
    
    def __str__(self):
        return f"{self.alt or 'Image'} - {self.src[:50]}"


class ContentType(models.Model):
    """
    Types de contenu détectés sur un site.
    """
    analysis = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='content_types')
    
    type_id = models.CharField(max_length=100)  # products, articles, etc.
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=10, default='📦')
    
    # Informations de détection
    count = models.IntegerField(default=0)
    selector = models.CharField(max_length=500, blank=True, null=True)
    detected_fields = models.JSONField(default=list, blank=True)  # Liste des champs détectés
    
    # Exemples de données
    preview_items = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'content_types'
        verbose_name = 'Type de contenu'
        verbose_name_plural = 'Types de contenu'
    
    def __str__(self):
        return f"{self.title} ({self.count} items)"


class ApiKey(models.Model):
    """
    Clés API pour l'accès programmatique.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=64, unique=True)
    key_prefix = models.CharField(max_length=8)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'Clé API'
        verbose_name_plural = 'Clés API'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"


class Webhook(models.Model):
    """
    Webhooks pour notifications en temps réel.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webhooks')
    url = models.URLField(max_length=2000)
    events = models.JSONField(default=list)  # Liste des événements: scraping.started, etc.
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    # Statistiques
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'webhooks'
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.url[:50]} - {len(self.events)} événements"
