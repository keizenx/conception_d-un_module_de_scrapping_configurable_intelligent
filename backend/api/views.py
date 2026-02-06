# backend/api/views.py
# ViewSets Django REST Framework pour toutes les routes API
# Gère l'authentification, le scraping, l'analyse et les rapports
# RELEVANT FILES: api/serializers.py, api/models.py, api/urls.py, config/urls.py

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from django.utils import timezone
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta
import json
import csv
import io

from .models import User, ScrapingSession, ScrapedData, Report, ApiKey, Webhook
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ScrapingSessionSerializer, CreateScrapingSessionSerializer,
    ScrapedDataSerializer, ReportSerializer, CreateReportSerializer,
    ApiKeySerializer, CreateApiKeySerializer,
    WebhookSerializer, CreateWebhookSerializer
)

import sys
import os
# Ajout du chemin src pour importer le scraper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.scraper import scrape_url
    from core.analyzer import analyze_url
    from core.subdomain_finder import discover_subdomains
    from core.site_checker import SiteChecker, filter_scrapable_sites
    from core.path_finder import discover_paths
    from core.smart_crawler import discover_paths_smart
    SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    scrape_url = None
    analyze_url = None
    discover_subdomains = None
    discover_paths = None
    discover_paths_smart = None
    SiteChecker = None
    filter_scrapable_sites = None
    SCRAPER_AVAILABLE = False
    discover_subdomains = None
    SiteChecker = None
    filter_scrapable_sites = None
    SCRAPER_AVAILABLE = False


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet pour l'authentification : login, register, logout.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Inscription d'un nouvel utilisateur.
        POST /api/auth/register/
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False # Désactiver le compte jusqu'à vérification
            
            # Générer code de vérification
            code = ''.join(random.choices(string.digits, k=6))
            user.two_factor_code = code # On réutilise ce champ pour la vérification email
            user.save()
            
            # Envoyer email de vérification
            try:
                send_mail(
                    'Vérifiez votre email - Scraper Pro',
                    f'Bonjour {user.username},\n\nVotre code de vérification est : {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Erreur envoi email: {e}")
                # En cas d'erreur email, on pourrait supprimer le user ou renvoyer une erreur
                # Pour l'instant, on laisse faire (mais l'user ne pourra pas vérifier)
            
            return Response({
                'message': 'Compte créé. Veuillez vérifier votre email.',
                'email': user.email,
                'verification_required': True
            }, status=status.HTTP_201_CREATED)
            
        print(f"Register validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='verify-email')
    def verify_email(self, request):
        """
        Vérifie l'email après inscription.
        POST /api/auth/verify-email/
        """
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
             return Response({'error': 'Email et code requis'}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            # On cherche un utilisateur inactif avec cet email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.is_active:
            return Response({'message': 'Compte déjà actif'}, status=status.HTTP_200_OK)
            
        if user.two_factor_code != code:
            return Response({'error': 'Code incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Activer le compte
        user.is_active = True
        user.two_factor_code = None
        user.is_email_verified = True # Si on utilise ce champ
        user.save()
        
        # Connecter l'utilisateur
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Email vérifié, compte activé'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Connexion d'un utilisateur.
        POST /api/auth/login/
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Vérifier si 2FA est activé
            if user.is_2fa_enabled:
                # Générer un code
                code = ''.join(random.choices(string.digits, k=6))
                user.two_factor_code = code
                user.two_factor_code_expires = timezone.now() + timedelta(minutes=10)
                user.save(update_fields=['two_factor_code', 'two_factor_code_expires'])
                
                # Envoyer l'email
                try:
                    send_mail(
                        'Code de vérification 2FA - Scraper Pro',
                        f'Votre code de vérification est : {code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    return Response({
                        'error': 'Erreur lors de l\'envoi du code email'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                return Response({
                    '2fa_required': True,
                    'message': 'Code 2FA envoyé par email'
                }, status=status.HTTP_200_OK)
            
            # Mettre à jour last_login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Connexion réussie'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='verify-2fa')
    def verify_2fa(self, request):
        """
        Vérifie le code 2FA et connecte l'utilisateur.
        POST /api/auth/verify-2fa/
        """
        username = request.data.get('username')
        password = request.data.get('password')
        code = request.data.get('code')
        
        if not username or not password or not code:
            return Response({'error': 'Données incomplètes'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if not user:
             return Response({'error': 'Identifiants invalides'}, status=status.HTTP_400_BAD_REQUEST)
             
        if not user.is_2fa_enabled:
            return Response({'error': '2FA non activé pour cet utilisateur'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Vérifier le code
        if user.two_factor_code != code:
            return Response({'error': 'Code incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.two_factor_code_expires < timezone.now():
            return Response({'error': 'Code expiré'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Code valide, reset du code et login
        user.two_factor_code = None
        user.two_factor_code_expires = None
        user.last_login = timezone.now()
        user.save()
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Connexion 2FA réussie'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='enable-2fa')
    def enable_2fa(self, request):
        user = request.user
        user.is_2fa_enabled = True
        user.save()
        return Response({'message': '2FA activé avec succès'})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='disable-2fa')
    def disable_2fa(self, request):
        user = request.user
        user.is_2fa_enabled = False
        user.save()
        return Response({'message': '2FA désactivé avec succès'})

    @action(detail=False, methods=['post'], url_path='forgot-password')
    def forgot_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Pour sécurité, ne pas dire que l'user n'existe pas
            return Response({'message': 'Si l\'email existe, un code a été envoyé.'})
            
        # Générer code
        code = ''.join(random.choices(string.digits, k=6))
        user.two_factor_code = code
        user.two_factor_code_expires = timezone.now() + timedelta(minutes=15)
        user.save()
        
        # Envoyer email
        try:
            send_mail(
                'Réinitialisation de mot de passe - Scraper Pro',
                f'Votre code de réinitialisation est : {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'error': 'Erreur d\'envoi d\'email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({'message': 'Si l\'email existe, un code a été envoyé.'})

    @action(detail=False, methods=['post'], url_path='reset-password-confirm')
    def reset_password_confirm(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not email or not code or not new_password:
            return Response({'error': 'Données incomplètes'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.two_factor_code != code:
            return Response({'error': 'Code incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.two_factor_code_expires < timezone.now():
            return Response({'error': 'Code expiré'}, status=status.HTTP_400_BAD_REQUEST)
            
        if len(new_password) < 8:
            return Response({'error': 'Mot de passe trop court (min 8 car.)'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        user.two_factor_code = None
        user.two_factor_code_expires = None
        user.save()
        
        return Response({'message': 'Mot de passe réinitialisé avec succès'})
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Déconnexion d'un utilisateur.
        POST /api/auth/logout/
        """
        try:
            request.user.auth_token.delete()
        except:
            pass
        logout(request)
        return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Récupère les informations de l'utilisateur connecté.
        GET /api/auth/me/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated], url_path='profile')
    def profile(self, request):
        """
        Récupère ou met à jour le profil de l'utilisateur.
        GET/PUT /api/auth/profile/
        """
        user = request.user
        
        if request.method == 'GET':
            # Statistiques de l'utilisateur
            total_sessions = ScrapingSession.objects.filter(user=user).count()
            data_extracted = ScrapedData.objects.filter(session__user=user).count()
            
            # URL de l'avatar
            avatar_url = None
            if user.avatar:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            
            return Response({
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'bio': user.bio or '',
                'company': user.company or '',
                'avatar_url': avatar_url,
                'role': 'admin' if user.is_staff else 'user',
                'total_sessions': total_sessions,
                'data_extracted': data_extracted,
                'member_since': user.date_joined.strftime('%d/%m/%Y'),
                'last_login': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'N/A'
            })
        
        elif request.method == 'PUT':
            # Mise à jour du profil
            name = request.data.get('name', '')
            email = request.data.get('email', user.email)
            bio = request.data.get('bio', '')
            company = request.data.get('company', '')
            
            # Séparer le nom complet en prénom/nom
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.email = email
            
            # Si les champs bio et company existent dans le modèle
            if hasattr(user, 'bio'):
                user.bio = bio
            if hasattr(user, 'company'):
                user.company = company
            
            user.save()
            
            return Response({
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'email': user.email,
                'bio': getattr(user, 'bio', ''),
                'company': getattr(user, 'company', ''),
                'role': 'admin' if user.is_staff else 'user',
                'message': 'Profil mis à jour avec succès'
            })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='change-password')
    def change_password(self, request):
        """
        Modifie le mot de passe de l'utilisateur.
        POST /api/auth/change-password/
        """
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'detail': 'Mot de passe actuel et nouveau mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le mot de passe actuel
        if not user.check_password(current_password):
            return Response({
                'detail': 'Mot de passe actuel incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider le nouveau mot de passe
        if len(new_password) < 8:
            return Response({
                'detail': 'Le nouveau mot de passe doit contenir au moins 8 caractères'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Définir le nouveau mot de passe
        user.set_password(new_password)
        user.save()
        
        # Mettre à jour le token
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Mot de passe modifié avec succès',
            'token': token.key
        })
    
    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated], url_path='delete-account')
    def delete_account(self, request):
        """
        Supprime le compte de l'utilisateur.
        DELETE /api/auth/delete-account/
        """
        user = request.user
        
        # Supprimer toutes les données associées
        ScrapingSession.objects.filter(user=user).delete()
        Report.objects.filter(user=user).delete()
        ApiKey.objects.filter(user=user).delete()
        
        # Supprimer le token
        try:
            user.auth_token.delete()
        except:
            pass
        
        # Supprimer l'utilisateur
        user.delete()
        
        return Response({
            'message': 'Compte supprimé avec succès'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='upload-avatar')
    def upload_avatar(self, request):
        """
        Upload une photo de profil.
        POST /api/auth/upload-avatar/
        """
        user = request.user
        
        if 'avatar' not in request.FILES:
            return Response({
                'detail': 'Aucun fichier fourni'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # Vérifier le type de fichier
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({
                'detail': 'Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WebP.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier la taille (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({
                'detail': 'Le fichier est trop volumineux. Maximum 5 Mo.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Supprimer l'ancien avatar si existant
        if user.avatar:
            user.avatar.delete(save=False)
        
        # Sauvegarder le nouvel avatar
        user.avatar = avatar_file
        user.save()
        
        # Construire l'URL complète
        avatar_url = request.build_absolute_uri(user.avatar.url) if user.avatar else None
        
        return Response({
            'message': 'Photo de profil mise à jour',
            'avatar_url': avatar_url
        })
    
    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated], url_path='delete-avatar')
    def delete_avatar(self, request):
        """
        Supprime la photo de profil.
        DELETE /api/auth/delete-avatar/
        """
        user = request.user
        
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            
            return Response({
                'message': 'Photo de profil supprimée'
            })
        
        return Response({
            'detail': 'Aucune photo de profil à supprimer'
        }, status=status.HTTP_400_BAD_REQUEST)


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet pour les statistiques du Dashboard.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Récupère les statistiques globales pour le dashboard.
        GET /api/dashboard/stats/
        """
        user = request.user
        
        # Sessions totales
        total_sessions = ScrapingSession.objects.filter(user=user).count()
        
        # Sessions complétées
        completed_sessions = ScrapingSession.objects.filter(
            user=user, 
            status='completed'
        ).count()
        
        # Données extraites totales
        extracted_data = ScrapedData.objects.filter(
            session__user=user
        ).count()
        
        # Calcul du taux de succès
        if total_sessions > 0:
            success_rate = round((completed_sessions / total_sessions) * 100, 1)
        else:
            success_rate = 0
        
        # Temps moyen de scraping
        from django.db.models import Avg, F, ExpressionWrapper, fields
        from datetime import timedelta
        
        avg_duration = ScrapingSession.objects.filter(
            user=user,
            status='completed',
            completed_at__isnull=False
        ).annotate(
            duration=ExpressionWrapper(
                F('completed_at') - F('started_at'),
                output_field=fields.DurationField()
            )
        ).aggregate(avg=Avg('duration'))['avg']
        
        if avg_duration:
            total_seconds = int(avg_duration.total_seconds())
            if total_seconds < 60:
                avg_time = f"{total_seconds}s"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                avg_time = f"{minutes}m {total_seconds % 60}s"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                avg_time = f"{hours}h {minutes}m"
        else:
            avg_time = "0s"
        
        return Response({
            'total_sessions': total_sessions,
            'extracted_data': extracted_data,
            'success_rate': success_rate,
            'avg_time': avg_time,
            'completed_sessions': completed_sessions
        })
    
    @action(detail=False, methods=['get'])
    def recent_sessions(self, request):
        """
        Récupère les sessions récentes de l'utilisateur.
        GET /api/dashboard/recent_sessions/
        """
        sessions = ScrapingSession.objects.filter(
            user=request.user
        ).order_by('-started_at')[:10]
        
        serializer = ScrapingSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """
        Récupère les données d'activité pour le graphique.
        GET /api/dashboard/activity/
        """
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        from datetime import datetime, timedelta
        
        # Derniers 7 jours
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)
        
        # Compter les sessions par jour
        activity = ScrapingSession.objects.filter(
            user=request.user,
            started_at__date__gte=start_date,
            started_at__date__lte=end_date
        ).annotate(
            date=TruncDate('started_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Créer un dictionnaire avec tous les jours
        all_days = {}
        current_date = start_date
        while current_date <= end_date:
            all_days[current_date] = 0
            current_date += timedelta(days=1)
        
        # Remplir avec les données réelles
        for item in activity:
            all_days[item['date']] = item['count']
        
        # Formater pour le frontend
        labels = []
        data = []
        for date, count in sorted(all_days.items()):
            labels.append(date.strftime('%d/%m'))
            data.append(count)
        
        return Response({
            'labels': labels,
            'data': data
        })


class AnalysisViewSet(viewsets.ViewSet):
    """
    ViewSet pour l'analyse d'URL avant scraping.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def quick_analyze(self, request):
        """
        Analyse rapide publique (sans authentification) pour la landing page.
        Résultats limités pour inciter à l'inscription.
        POST /api/analysis/quick_analyze/
        Body: { "url": "https://example.com" }
        """
        url = request.data.get('url')
        
        if not url:
            return Response({'error': 'URL requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Analyse basique
            site_check = None
            if SCRAPER_AVAILABLE and SiteChecker:
                checker = SiteChecker(timeout=10)
                site_check = checker.check_site(url)
                
                if not site_check['scrapable']:
                    return Response({
                        'success': False,
                        'error': 'Site protégé ou inaccessible',
                        'url': url,
                        'page_count': 0,
                        'content_types_count': 0,
                        'requires_login': True
                    }, status=status.HTTP_200_OK)
            
            # Découverte limitée (max 10 pages)
            paths_data = None
            if SCRAPER_AVAILABLE and discover_paths_smart:
                paths_result = discover_paths_smart(url, max_pages=10)
                
                if paths_result.get('paths'):
                    paths_data = {
                        'total_found': paths_result.get('total_paths', 0),
                    }
            
            # Analyse de contenu limitée
            content_types_count = 0
            if SCRAPER_AVAILABLE and analyze_url:
                result = analyze_url(url, max_candidates=3, max_items_preview=2, use_js=True)
                if result.get('collections'):
                    content_types_count = len(result['collections'])
            
            return Response({
                'success': True,
                'url': url,
                'page_count': paths_data.get('total_found', 1) if paths_data else 1,
                'subdomains': {'total_found': 0},
                'content_types': [],
                'content_types_count': content_types_count,
                'requires_login': True,
                'message': 'Connectez-vous pour voir l\'analyse complète'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Erreur lors de l'analyse rapide: {e}")
            return Response({
                'error': str(e),
                'requires_login': True
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Analyse une URL pour détecter les patterns et la structure.
        Crée une session et enregistre les logs de progression.
        Retourne immédiatement le session_id et lance l'analyse en arrière-plan.
        POST /api/analysis/analyze/
        Body: { 
            "url": "https://example.com", 
            "include_subdomains": false,
            "advanced_options": {...}
        }
        """
        url = request.data.get('url')
        include_subdomains = request.data.get('include_subdomains', False)
        advanced_options = request.data.get('advanced_options', {})
        
        if not url:
            return Response({'error': 'URL requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Configuration avec options avancées
        config = {
            'include_subdomains': include_subdomains,
            'depth': advanced_options.get('depth', 2),
            'delay': advanced_options.get('delay', 500),
            'user_agent': advanced_options.get('user_agent', 'Chrome (Desktop)'),
            'timeout': advanced_options.get('timeout', 30),
            'custom_selectors': advanced_options.get('custom_selectors', [])
        }
        
        # Créer une session de scraping pour tracker les logs
        session = ScrapingSession.objects.create(
            user=request.user,
            url=url,
            status='in_progress',
            configuration=config
        )
        
        # Lancer l'analyse en arrière-plan
        from threading import Thread
        
        session_id = session.id
        def run_analysis():
            self._run_analysis_task(session_id, url, config)
        
        thread = Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        # Retourner immédiatement le session_id
        return Response({
            'success': True,
            'session_id': session.id,
            'message': 'Analyse démarrée'
        })
    
    def _run_analysis_task(self, session_id, url, config):
        """
        Exécute l'analyse complète en arrière-plan.
        
        Args:
            session_id: ID de la session
            url: URL à analyser
            config: Configuration avec options avancées (depth, delay, timeout, etc.)
        """
        from .models import ScrapingSession
        
        try:
            session = ScrapingSession.objects.get(id=session_id)
        except ScrapingSession.DoesNotExist:
            return
        
        # Extraire les options
        include_subdomains = config.get('include_subdomains', False)
        timeout = config.get('timeout', 30)
        
        try:
            # Étape 1: Vérifier que le site est accessible et scrapable
            site_check = None
            if SCRAPER_AVAILABLE and SiteChecker:
                session.add_log(f"[*] Vérification de l'accessibilité de {url}...")
                checker = SiteChecker(timeout=timeout)  # Utiliser timeout des options
                site_check = checker.check_site(url)
                
                # Si le site n'est pas scrapable, marquer la session comme échouée
                if not site_check['scrapable']:
                    session.add_log(f"[!] Site protégé ou inaccessible: {site_check.get('status_info', {}).get('message', 'Erreur')}", 'warning')
                    session.mark_failed('Site non scrapable')
                    return
                
                session.add_log(f"[✓] Site accessible et scrapable", 'success')
            
            # Étape 2: Découverte de sous-domaines si demandée
            subdomains_data = None
            if include_subdomains and SCRAPER_AVAILABLE and discover_subdomains:
                session.add_log(f"[*] Découverte de sous-domaines...")
                subdomains_result = discover_subdomains(
                    url, 
                    use_crtsh=True,
                    use_hackertarget=True,
                    use_dnsrepo=False,
                    use_common=False,
                    max_subdomains=50
                )
                
                # Vérifier les sous-domaines scrapables
                if subdomains_result.get('subdomains') and SiteChecker:
                    session.add_log(f"[*] Vérification de {len(subdomains_result['subdomains'])} sous-domaines...")
                    subdomains_to_check = subdomains_result['subdomains'][:20]
                    
                    scrapable_list, non_scrapable_list, check_details = filter_scrapable_sites(subdomains_to_check)
                    
                    from urllib.parse import urlparse
                    scrapable_domains = [urlparse(u).netloc for u in scrapable_list]
                    non_scrapable_domains = [urlparse(u).netloc for u in non_scrapable_list]
                    
                    check_details_by_domain = {
                        urlparse(u).netloc: {
                            'scrapable': details['scrapable'],
                            'status': details['status_code'],
                            'protection': details.get('protections', [None])[0] if details.get('protections') else None,
                            'tech_stack': details.get('tech_stack', []),
                            'status_info': details.get('status_info', {})
                        }
                        for u, details in check_details.items()
                    }
                    
                    subdomains_data = {
                        'total_found': subdomains_result.get('total_found', 0),
                        'total_checked': len(subdomains_to_check),
                        'scrapable_count': len(scrapable_domains),
                        'scrapable_list': scrapable_domains,
                        'non_scrapable_count': len(non_scrapable_domains),
                        'all_subdomains': subdomains_result.get('subdomains', []),
                        'sources': subdomains_result.get('sources', []),
                        'check_details': check_details_by_domain
                    }
                    session.add_log(f"[✓] {len(scrapable_domains)} sous-domaines scrapables trouvés", 'success')
            
            # Étape 2b: Crawling intelligent avec Playwright
            paths_data = None
            if SCRAPER_AVAILABLE and discover_paths_smart:
                # Étape préliminaire: Estimer le nombre de pages
                session.add_log(f"[*] Estimation du nombre de pages du site...")
                from src.core.site_estimator import SiteEstimator
                
                estimator = SiteEstimator(url)
                estimation = estimator.estimate_total_pages()
                
                estimated_pages = estimation['estimated_pages']
                confidence = estimation['confidence']
                method = estimation['method']
                recommended_max = estimation['recommended_max_crawl']
                
                session.add_log(
                    f"📊 Estimation: ~{estimated_pages} pages (confiance: {confidence}, méthode: {method})",
                    'info'
                )
                
                # Ajuster le nombre de pages à crawler
                max_pages_to_crawl = min(recommended_max, 100)  # Maximum absolu de 100
                
                session.add_log(f"[*] Crawl intelligent du site avec Playwright...")
                session.add_log(f"🕷️ Lancement du Smart Crawler (max {max_pages_to_crawl} pages sur ~{estimated_pages})...", 'info')
                
                # Lancer le crawling avec la limite adaptative
                paths_result = discover_paths_smart(url, max_pages=max_pages_to_crawl)
                
                # Logger les pages découvertes (après le crawling)
                if paths_result.get('all_pages'):
                    session.add_log(f"📄 {len(paths_result['all_pages'])} pages découvertes:", 'success')
                    for idx, page_info in enumerate(paths_result['all_pages'][:10]):  # Limiter à 10 pour pas surcharger les logs
                        session.add_log(f"  └─ {page_info.get('url', '')}")
                    if len(paths_result['all_pages']) > 10:
                        session.add_log(f"  └─ ... et {len(paths_result['all_pages']) - 10} autres pages")
                
                if paths_result.get('paths'):
                    all_pages_with_preview = []
                    for page_info in paths_result.get('all_pages', []):
                        all_pages_with_preview.append({
                            'url': page_info.get('url', ''),
                            'title': page_info.get('title', ''),
                            'preview': page_info.get('preview', {})
                        })
                    
                    paths_data = {
                        'total_found': paths_result.get('total_paths', 0),
                        'pages_crawled': paths_result.get('pages_crawled', 0),
                        'paths': paths_result.get('paths', []),
                        'main_pages': paths_result.get('main_pages', []),
                        'all_pages': all_pages_with_preview,
                        'navigation': paths_result.get('navigation', {})
                    }
                    session.add_log(f"[✓] {paths_result.get('pages_crawled', 0)} pages crawlées avec succès", 'success')
            
            # Étape 3: Analyser le contenu avec Perplexity pour identification intelligente
            content_types = {}  # Utiliser un dict pour regrouper par type
            scrapable_content_data = None
            if SCRAPER_AVAILABLE and analyze_url:
                session.add_log(f"[*] Analyse du contenu avec IA...")
                
                # Analyser la page principale
                result = analyze_url(url, max_candidates=5, max_items_preview=3, use_js=True)
                
                # Si pas de contenu, essayer d'autres pages
                if not result.get('collections') and paths_data and paths_data.get('main_pages'):
                    session.add_log(f"[*] Analyse des pages secondaires...")
                    for page in paths_data['main_pages'][:3]:
                        try:
                            page_url = page.get('url', '')
                            if page_url and page_url != url:
                                session.add_log(f"    └─ Analyse de {page_url}...")
                                result = analyze_url(page_url, max_candidates=5, max_items_preview=3, use_js=True)
                                if result.get('collections'):
                                    session.add_log(f"    └─ ✓ Contenu trouvé", 'success')
                                    break
                        except:
                            continue
                
                # Utiliser Perplexity pour classifier intelligemment
                from src.core.perplexity_classifier import PerplexityClassifier
                perplexity = PerplexityClassifier()
                
                if result.get('collections'):
                    for i, collection in enumerate(result['collections'][:6]):
                        # Collecter les champs détectés
                        detected_types = set()
                        sample_text = ""
                        for item in collection.get('items_preview', []):
                            for field in item.get('fields', []):
                                detected_types.add(field.get('type', 'text'))
                                if field.get('value') and len(sample_text) < 300:
                                    sample_text += str(field.get('value')) + " "
                        
                        # Classification IA avec Perplexity
                        classification = perplexity.classify_content(
                            url=url,
                            page_title=result.get('page_title', ''),
                            sample_text=sample_text,
                            detected_fields=list(detected_types)
                        )
                        
                        session.add_log(f"[Intelligent] Type identifié: {classification.get('title', 'Inconnu')} (confiance: {classification.get('confidence', 0):.0%})", 'info')
                        
                        content_type_key = classification.get('type', 'content')
                        
                        # Regrouper par type au lieu de créer des doublons
                        if content_type_key in content_types:
                            # Incrémenter le count si le type existe déjà
                            content_types[content_type_key]['count'] += collection.get('count', 0)
                        else:
                            # Créer un nouveau type
                            content_types[content_type_key] = {
                                'id': content_type_key,
                                'icon': classification.get('icon', 'public'),
                                'title': classification.get('title', 'Contenu'),
                                'count': collection.get('count', 0),
                                'confidence': classification.get('confidence', 0.5),
                                'description': classification.get('description', ''),
                                'sample_items': []
                            }
                        
                        # Ajouter les items preview
                        for item in collection.get('items_preview', [])[:3]:
                            content_types[content_type_key]['sample_items'].append({
                                'url': item.get('url', '#'),
                                'fields': item.get('fields', [])
                            })
                
                # Extraire les données de scrapable_content si disponibles
                if result and result.get('scrapable_content'):
                    scrapable = result['scrapable_content']
                    scrapable_content_data = {
                        'detected_types': scrapable.get('detected_types', []),
                        'total_types': scrapable.get('total_types', 0),
                        'structure_complexity': scrapable.get('structure_complexity', 'simple'),
                        'has_pagination': scrapable.get('has_pagination', False),
                        'recommended_action': scrapable.get('recommended_action', 'full_crawl'),
                        'rejected_types': scrapable.get('rejected_types', []),
                        'ai_validation': scrapable.get('ai_validation', {})
                    }
                    session.add_log(f"[✓] {scrapable.get('total_types', 0)} types de contenu détectés: {', '.join([t['name'] for t in scrapable.get('detected_types', [])])}", 'info')
                
                # Convertir le dict en liste pour la compatibilité
                content_types_list = list(content_types.values())
                session.add_log(f"[✓] {len(content_types_list)} types de contenu identifiés", 'success')
            
            # Sauvegarder les résultats dans la configuration de la session
            config = session.configuration or {}
            config['content_types'] = content_types_list
            config['scrapable_content'] = scrapable_content_data
            config['subdomains'] = subdomains_data
            config['paths'] = paths_data
            config['site_check'] = {
                'accessible': site_check.get('accessible') if site_check else False,
                'scrapable': site_check.get('scrapable') if site_check else False,
                'status_code': site_check.get('status_code') if site_check else None,
                'protections': site_check.get('protections', []) if site_check else [],
                'tech_stack': site_check.get('tech_stack', []) if site_check else [],
                'server': site_check.get('server') if site_check else None,
                'status_info': site_check.get('status_info', {}) if site_check else {}
            } if site_check else {}
            session.configuration = config
            
            # Marquer la session comme terminée
            session.add_log(f"[✓] Analyse terminée avec succès!", 'success')
            session.total_items = paths_data.get('pages_crawled', 0) if paths_data else 0
            session.mark_completed()
            
        except Exception as e:
            import traceback
            session.add_log(f"[!] Erreur: {str(e)}", 'error')
            session.add_log(f"{traceback.format_exc()}", 'error')
            session.mark_failed(str(e))


class ScrapingViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les sessions de scraping.
    """
    serializer_class = ScrapingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne uniquement les sessions de l'utilisateur connecté."""
        return ScrapingSession.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def latest(self, request):
        """
        Récupère la dernière session de scraping de l'utilisateur.
        GET /api/scraping/latest/
        """
        try:
            if request.user.is_authenticated:
                session = ScrapingSession.objects.filter(user=request.user).order_by('-started_at').first()
            else:
                # Pour le dev, retourner la dernière session globale
                session = ScrapingSession.objects.order_by('-started_at').first()
            
            if not session:
                return Response({'error': 'Aucune session trouvée'}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'session_id': session.id,
                'url': session.url,
                'status': session.status,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'total_items': session.scraped_data.count()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def logs(self, request, pk=None):
        """
        Récupère les logs de progression d'une session.
        GET /api/scraping/{id}/logs/
        """
        try:
            # Récupérer directement la session sans filtrer par user (pour le dev)
            session = ScrapingSession.objects.get(pk=pk)
            return Response({
                'logs': session.progress_logs or [],
                'current_step': session.current_step,
                'status': session.status
            })
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def status(self, request, pk=None):
        """
        Récupère le statut d'une session de scraping (pour le polling async).
        GET /api/scraping/{id}/status/
        """
        try:
            session = ScrapingSession.objects.get(pk=pk)
            
            # Calculer le nombre d'éléments scrapés
            total_items = session.scraped_data.count() if hasattr(session, 'scraped_data') else 0
            
            # Calculer la progression (estimation basée sur les logs)
            logs = session.progress_logs or []
            progress = 0
            if session.status == 'completed':
                progress = 100
            elif session.status == 'failed':
                progress = 0
            elif logs:
                # Estimation basée sur les étapes connues
                progress = min(len(logs) * 15, 95)  # Max 95% jusqu'à completion
            
            return Response({
                'id': session.id,
                'status': session.status,
                'url': session.url,
                'progress': progress,
                'current_step': session.current_step,
                'total_items': total_items,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'error_message': session.error_message,
                'logs': logs[-5:] if logs else []  # Derniers 5 logs
            })
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def results(self, request, pk=None):
        """
        Récupère les résultats complets d'une analyse terminée.
        GET /api/scraping/{id}/results/
        """
        try:
            # Récupérer directement la session sans filtrer par user (pour le dev)
            session = ScrapingSession.objects.get(pk=pk)
            
            # Récupérer les résultats de la configuration sauvegardée
            config = session.configuration or {}
            
            return Response({
                'status': session.status,
                'url': session.url,
                'content_types': config.get('content_types', []),
                'scrapable_content': config.get('scrapable_content', None),
                'subdomains': config.get('subdomains', {}),
                'paths': config.get('paths', {}),
                'site_check': config.get('site_check', {}),
                'page_count': session.total_items or 0,
                'completed_at': session.completed_at,
                'error_message': session.error_message
            })
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def rescrape(self, request, pk=None):
        """
        Re-scrape un site à partir d'une session existante.
        POST /api/scraping/{id}/rescrape/
        Crée une nouvelle session avec la même configuration et relance le scraping.
        """
        try:
            # Récupérer la session originale
            original_session = ScrapingSession.objects.get(pk=pk)
            
            # Déterminer l'utilisateur
            if request.user.is_authenticated:
                user = request.user
            else:
                user = original_session.user
            
            # Créer une nouvelle session avec la même configuration
            new_session = ScrapingSession.objects.create(
                user=user,
                url=original_session.url,
                status='in_progress',
                configuration=original_session.configuration.copy() if original_session.configuration else {}
            )
            
            new_session.add_log(f"[*] Re-scraping de {original_session.url}", 'info')
            new_session.add_log(f"[*] Basé sur la session #{original_session.id}", 'info')
            
            # Lancer le scraping en arrière-plan (même logique que start)
            from threading import Thread
            
            def run_scraping():
                try:
                    from src.core.analyzer import analyze_url
                    from src.core.fetcher_playwright import fetch_html_smart
                    from bs4 import BeautifulSoup
                    
                    url = new_session.url
                    config = new_session.configuration
                    selected_types = config.get('content_types', [])
                    timeout = config.get('timeout', 30)
                    
                    new_session.add_log(f"[*] Récupération du HTML...", 'info')
                    html_content = fetch_html_smart(url, use_js=True, timeout_seconds=float(timeout))
                    
                    if html_content:
                        new_session.add_log(f"[*] HTML récupéré ({len(html_content)} caractères)", 'info')
                        
                        # Analyser et extraire
                        result = analyze_url(url, max_candidates=10, max_items_preview=10, use_js=True)
                        
                        if result and result.get('scrapable_content'):
                            # Sauvegarder les résultats (même logique que start)
                            new_session.configuration['scrapable_content'] = result.get('scrapable_content')
                            new_session.status = 'completed'
                            new_session.completed_at = timezone.now()
                            new_session.add_log(f"[✓] Re-scraping terminé avec succès", 'success')
                        else:
                            new_session.status = 'completed'
                            new_session.completed_at = timezone.now()
                            new_session.add_log(f"[!] Aucun contenu scrapable trouvé", 'warning')
                    else:
                        new_session.mark_failed("Impossible de récupérer le HTML")
                    
                    new_session.save()
                except Exception as e:
                    new_session.mark_failed(str(e))
            
            # Lancer en thread pour ne pas bloquer
            thread = Thread(target=run_scraping)
            thread.start()
            
            return Response({
                'message': 'Re-scraping lancé',
                'new_session_id': new_session.id,
                'original_session_id': original_session.id,
                'url': original_session.url
            }, status=status.HTTP_201_CREATED)
            
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def start(self, request):
        """
        Démarre une nouvelle session de scraping avec les types sélectionnés.
        POST /api/scraping/start/
        Body: { 
            "url": "https://example.com", 
            "content_types": [...],
            "depth": 2,
            "delay": 500,
            ...
        }
        """
        url = request.data.get('url')
        if not url:
            return Response({'error': 'URL requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        selected_types = request.data.get('content_types', [])
        
        # Créer une session de scraping
        # Utiliser l'utilisateur connecté, sinon un utilisateur de test
        if request.user.is_authenticated:
            user = request.user
            print(f"[DEBUG] Session créée pour l'utilisateur authentifié: {user.username}")
        else:
            # Créer ou récupérer un utilisateur de test
            test_user, created = User.objects.get_or_create(
                username='test_scraper',
                defaults={'email': 'test@scraper.com'}
            )
            user = test_user
            print(f"[DEBUG] Session créée pour l'utilisateur de test: {user.username}")
            
        session = ScrapingSession.objects.create(
            user=user,
            url=url,
            status='in_progress',
            configuration={
                'content_types': selected_types,
                'depth': request.data.get('depth', 2),
                'delay': request.data.get('delay', 500),
                'user_agent': request.data.get('user_agent', 'Chrome (Desktop)'),
                'timeout': request.data.get('timeout', 30),
                'custom_selectors': request.data.get('custom_selectors', {}),
                'export_format': request.data.get('export_format', 'json'),
            }
        )
        
        session.add_log(f"[*] Démarrage du scraping pour {url}", 'info')
        session.add_log(f"[*] Types sélectionnés: {selected_types}", 'info')
        
        # Récupérer les options avancées de la configuration
        config = session.configuration
        depth = config.get('depth', 2)
        delay = config.get('delay', 500)
        user_agent = config.get('user_agent', 'Chrome (Desktop)')
        timeout = config.get('timeout', 30)
        custom_selectors = config.get('custom_selectors', [])
        
        session.add_log(f"[*] Options avancées: profondeur={depth}, délai={delay}ms, timeout={timeout}s", 'info')
        if custom_selectors:
            session.add_log(f"[*] Sélecteurs personnalisés: {len(custom_selectors)}", 'info')
        
        # Lancer le scraping des types sélectionnés
        try:
            # Importer les modules nécessaires
            from src.core.analyzer import analyze_url
            from src.core.content_detector import ContentDetector
            from src.core.fetcher_playwright import fetch_html_smart
            from bs4 import BeautifulSoup
            import time as time_module
            
            session.add_log(f"[*] Récupération du contenu HTML réel...", 'info')
            
            # Récupérer le HTML réel avec Playwright (utiliser le timeout configuré)
            html_content = fetch_html_smart(url, use_js=True, timeout_seconds=float(timeout))
            if not html_content:
                session.add_log("[!] Impossible de récupérer le contenu HTML", 'error')
                raise Exception("Échec de récupération HTML")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            session.add_log(f"[*] HTML récupéré ({len(html_content)} caractères)", 'info')
            
            # Appliquer le délai configuré entre requêtes
            if delay > 0:
                time_module.sleep(delay / 1000.0)  # Convertir ms en secondes
            
            # Analyser le contenu pour détecter les types
            result = analyze_url(url, max_candidates=10, max_items_preview=10, use_js=True)
            
            scraped_data = []
            total_extracted = 0
            
            # Extraire les données avec les sélecteurs personnalisés si fournis
            if custom_selectors:
                session.add_log(f"[*] Extraction avec sélecteurs personnalisés...", 'info')
                for selector_config in custom_selectors:
                    selector_name = selector_config.get('name', 'Champ')
                    css_selector = selector_config.get('selector', '')
                    if css_selector:
                        try:
                            elements = soup.select(css_selector)
                            if elements:
                                custom_items = []
                                for elem in elements[:50]:  # Limiter à 50 éléments
                                    custom_items.append({
                                        'text': elem.get_text(strip=True),
                                        'html': str(elem)[:500]
                                    })
                                
                                scraped_data.append({
                                    'category': f'custom_{selector_name.lower().replace(" ", "_")}',
                                    'category_fr': selector_name,
                                    'icon': '🎯',
                                    'count': len(custom_items),
                                    'items': custom_items
                                })
                                session.add_log(f"[*] Sélecteur '{selector_name}': {len(custom_items)} éléments trouvés", 'info')
                                total_extracted += len(custom_items)
                        except Exception as sel_err:
                            session.add_log(f"[!] Erreur sélecteur '{selector_name}': {str(sel_err)}", 'warning')
            
            if result and result.get('scrapable_content'):
                scrapable = result['scrapable_content']
                detected_types = scrapable.get('detected_types', [])
                
                # Debug: afficher les types détectés vs sélectionnés
                session.add_log(f"[DEBUG] Types détectés: {[t.get('type') for t in detected_types]}", 'info')
                session.add_log(f"[DEBUG] Types sélectionnés: {selected_types}", 'info')
                
                for detected_type in detected_types:
                    type_name = detected_type.get('type', '')
                    type_display_name = detected_type.get('name', '')
                    
                    # Vérifier si ce type est dans les types sélectionnés OU si aucun type n'est sélectionné
                    should_extract = False
                    if not selected_types:  # Si aucun type sélectionné, extraire tout
                        should_extract = True
                    else:  # Sinon, vérifier si le type est sélectionné
                        should_extract = type_name in selected_types
                    
                    if should_extract:
                        session.add_log(f"[*] Extraction de {type_display_name}...", 'info')
                        
                        # Extraire les vraies données selon le type
                        if type_name == 'media':
                            # Récupérer TOUTES les images et médias
                            media_elements = []
                            media_urls_seen = set()  # Éviter les doublons
                            
                            # Images
                            images = soup.find_all('img')
                            # Vidéos
                            videos = soup.find_all('video')
                            # Sources de vidéo
                            video_sources = soup.find_all('source')
                            # Liens vers médias
                            media_links = soup.find_all('a', href=True)
                            
                            session.add_log(f"[*] Médias trouvés - Images: {len(images)}, Vidéos: {len(videos)}, Sources: {len(video_sources)}", 'info')
                            
                            # Traiter les images
                            for img in images:
                                src = img.get('src', '') or img.get('data-src', '') or img.get('data-original', '')
                                if src and src not in media_urls_seen:
                                    media_urls_seen.add(src)
                                    alt = img.get('alt', '')
                                    title = img.get('title', alt)
                                    
                                    # Construire URL absolue
                                    if src.startswith('/'):
                                        from urllib.parse import urljoin
                                        src = urljoin(url, src)
                                    
                                    media_elements.append({
                                        'src': src,
                                        'alt': alt,
                                        'title': title or f'Image',
                                        'type': 'image',
                                        'element': img
                                    })
                            
                            # Traiter les vidéos
                            for video in videos:
                                src = video.get('src', '')
                                if src and src not in media_urls_seen:
                                    media_urls_seen.add(src)
                                    title = video.get('title', 'Vidéo')
                                    
                                    if src.startswith('/'):
                                        from urllib.parse import urljoin
                                        src = urljoin(url, src)
                                    
                                    media_elements.append({
                                        'src': src,
                                        'alt': '',
                                        'title': title,
                                        'type': 'video',
                                        'element': video
                                    })
                            
                            # Traiter les sources de vidéo
                            for source in video_sources:
                                src = source.get('src', '')
                                if src and src not in media_urls_seen:
                                    media_urls_seen.add(src)
                                    media_type = source.get('type', 'video')
                                    
                                    if src.startswith('/'):
                                        from urllib.parse import urljoin
                                        src = urljoin(url, src)
                                    
                                    media_elements.append({
                                        'src': src,
                                        'alt': '',
                                        'title': f'Source {media_type}',
                                        'type': 'source',
                                        'element': source
                                    })
                            
                            # Traiter les liens vers médias (pdf, images, etc.)
                            for link in media_links:
                                href = link.get('href', '')
                                if href and any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.mp4', '.avi']):
                                    if href not in media_urls_seen:
                                        media_urls_seen.add(href)
                                        
                                        if href.startswith('/'):
                                            from urllib.parse import urljoin
                                            href = urljoin(url, href)
                                        
                                        media_elements.append({
                                            'src': href,
                                            'alt': link.get_text(strip=True)[:50],
                                            'title': link.get_text(strip=True) or 'Fichier média',
                                            'type': 'link',
                                            'element': link
                                        })
                            
                            session.add_log(f"[*] {len(media_elements)} médias uniques trouvés (sans doublons)", 'info')
                            
                            # ==================== GROUPEMENT INTELLIGENT DES MÉDIAS ====================
                            # Grouper par type au lieu de créer une entrée par média
                            grouped_media = {
                                'images': [],
                                'videos': [],
                                'audios': [],
                                'documents': [],
                                'links': []
                            }
                            
                            for media in media_elements:
                                media_type = media['type']
                                if media_type == 'image':
                                    grouped_media['images'].append({
                                        'src': media['src'],
                                        'alt': media['alt'],
                                        'title': media['title']
                                    })
                                elif media_type == 'video':
                                    grouped_media['videos'].append({
                                        'src': media['src'],
                                        'title': media['title']
                                    })
                                elif media_type == 'audio':
                                    grouped_media['audios'].append({
                                        'src': media['src'],
                                        'title': media['title']
                                    })
                                elif media_type == 'link':
                                    if any(ext in media['src'].lower() for ext in ['.pdf', '.doc', '.xls', '.ppt']):
                                        grouped_media['documents'].append({
                                            'src': media['src'],
                                            'title': media['title']
                                        })
                                    else:
                                        grouped_media['links'].append({
                                            'src': media['src'],
                                            'title': media['title']
                                        })
                            
                            # Créer UNE entrée par type de média
                            media_info = {
                                'images': ('🖼️ Images', 'image'),
                                'videos': ('🎬 Vidéos', 'video'),
                                'audios': ('🎵 Audios', 'audio'),
                                'documents': ('📄 Documents', 'document'),
                                'links': ('🔗 Liens médias', 'link')
                            }
                            
                            for media_type, items in grouped_media.items():
                                if items:
                                    title, content_type = media_info[media_type]
                                    
                                    data_item = {
                                        'titre': f"{title} ({len(items)})",
                                        'type_media': content_type,
                                        'nb_elements': len(items),
                                        'elements': items,
                                        'apercu': ' | '.join([m['src'].split('/')[-1][:30] for m in items[:5]]) + ('...' if len(items) > 5 else '')
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type='grouped_media',
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                            
                            # Sauvegarder les images dans PageImage si PathDiscovery existe
                            try:
                                from .models import PathDiscovery, PageImage
                                # Chercher ou créer le path
                                path_obj, _ = PathDiscovery.objects.get_or_create(
                                    session=session,
                                    url=url,
                                    defaults={'title': soup.title.string if soup.title else 'Sans titre'}
                                )
                                
                                for img in grouped_media['images']:
                                    PageImage.objects.get_or_create(
                                        path=path_obj,
                                        src=img['src'][:2000],
                                        defaults={
                                            'alt': (img.get('alt') or '')[:500]
                                        }
                                    )
                                session.add_log(f"[*] {len(grouped_media['images'])} images sauvegardées dans PageImage", 'info')
                            except Exception as e:
                                session.add_log(f"[!] Erreur sauvegarde PageImage: {e}", 'warning')
                            
                            session.add_log(f"[*] Médias groupés en {len([m for m in grouped_media.values() if m])} catégories", 'info')
                        
                        elif type_name == 'text_content':
                            # Récupérer TOUS les textes possibles sans doublons INTELLIGENTS
                            text_elements_all = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'label', 'button', 'a', 'strong', 'em', 'b', 'i', 'small', 'code', 'pre', 'blockquote', 'cite', 'address', 'time', 'mark', 'ins', 'del', 'sub', 'sup', 'q', 'abbr', 'dfn', 'nav', 'aside', 'header', 'footer', 'main', 'section', 'article', 'figure', 'figcaption', 'caption', 'summary', 'details', 'menu', 'menuitem', 'input', 'textarea', 'select', 'option'])
                            texts_seen = set()  # Éviter les doublons INTELLIGENTS
                            valid_texts = []
                            
                            for elem in text_elements_all:
                                text = elem.get_text(strip=True)
                                
                                # DÉTECTION INTELLIGENTE DES DOUBLONS
                                # Nettoyer le texte pour comparaison
                                text_clean = ' '.join(text.split()).lower()  # Supprimer espaces multiples et normaliser
                                text_normalized = ''.join(c for c in text_clean if c.isalnum() or c.isspace())  # Garder que lettres/chiffres
                                
                                # Filtrer les textes valides avec détection avancée des doublons
                                if (text and 
                                    len(text.strip()) > 1 and  # Minimum 1 caractère utile
                                    len(text) < 5000 and  # Maximum 5000 caractères
                                    text_normalized not in texts_seen and  # Pas de doublons normalisés
                                    len(text_normalized.strip()) > 2 and  # Au moins 3 caractères après nettoyage
                                    text.strip() != ''):  # Pas complètement vide
                                    
                                    texts_seen.add(text_normalized)
                                    valid_texts.append({
                                        'element': elem,
                                        'text': text,
                                        'tag': elem.name
                                    })
                            
                            session.add_log(f"[*] {len(valid_texts)} textes uniques trouvés (détection intelligente)", 'info')
                            
                            # EXTRACTION SPÉCIALE pour les témoignages et contenus répétés
                            # Chercher des patterns spéciaux comme les témoignages
                            testimonials = soup.find_all(attrs={"class": lambda x: x and any(word in x.lower() for word in ["testimonial", "review", "comment", "quote"])})
                            faq_items = soup.find_all(attrs={"class": lambda x: x and any(word in x.lower() for word in ["faq", "question", "accordion", "collapse"])})
                            
                            if testimonials:
                                session.add_log(f"[*] {len(testimonials)} témoignages détectés", 'info')
                                for i, testimonial in enumerate(testimonials):
                                    test_text = testimonial.get_text(strip=True)
                                    if test_text and len(test_text) > 20:
                                        # Vérifier unicité pour témoignages
                                        test_normalized = ''.join(c for c in test_text.lower() if c.isalnum() or c.isspace())
                                        if test_normalized not in texts_seen:
                                            texts_seen.add(test_normalized)
                                            valid_texts.append({
                                                'element': testimonial,
                                                'text': test_text,
                                                'tag': testimonial.name or 'testimonial'
                                            })
                            
                            if faq_items:
                                session.add_log(f"[*] {len(faq_items)} éléments FAQ détectés", 'info')
                                for faq in faq_items:
                                    faq_text = faq.get_text(strip=True)
                                    if faq_text and len(faq_text) > 10:
                                        faq_normalized = ''.join(c for c in faq_text.lower() if c.isalnum() or c.isspace())
                                        if faq_normalized not in texts_seen:
                                            texts_seen.add(faq_normalized)
                                            valid_texts.append({
                                                'element': faq,
                                                'text': faq_text,
                                                'tag': faq.name or 'faq'
                                            })
                            
                            # Extraction spéciale pour les placeholders et valeurs de champs
                            form_elements = soup.find_all(['input', 'textarea', 'select', 'option'])
                            for form_elem in form_elements:
                                placeholder = form_elem.get('placeholder', '')
                                value = form_elem.get('value', '')
                                option_text = form_elem.get_text(strip=True) if form_elem.name in ['option', 'select'] else ''
                                
                                for field_text in [placeholder, value, option_text]:
                                    if field_text and len(field_text) > 1:
                                        field_normalized = ''.join(c for c in field_text.lower() if c.isalnum() or c.isspace())
                                        if field_normalized not in texts_seen:
                                            texts_seen.add(field_normalized)
                                            valid_texts.append({
                                                'element': form_elem,
                                                'text': field_text,
                                                'tag': f'{form_elem.name}_field'
                                            })
                            
                            # ==================== GROUPEMENT INTELLIGENT DES TEXTES ====================
                            # Grouper les textes par catégorie au lieu de créer une entrée par élément
                            grouped_content = {
                                'main_headings': [],      # h1
                                'section_headings': [],   # h2, h3
                                'sub_headings': [],       # h4, h5, h6
                                'paragraphs': [],         # p, div avec texte long
                                'links': [],              # a
                                'buttons': [],            # button
                                'lists': [],              # li
                                'navigation': [],         # nav
                                'footer': [],             # footer
                                'code': [],               # code, pre
                                'other': []               # reste
                            }
                            
                            for text_data in valid_texts:
                                text_content = text_data['text']
                                tag = text_data['tag']
                                
                                # Catégoriser le contenu
                                if tag == 'h1':
                                    grouped_content['main_headings'].append(text_content)
                                elif tag in ['h2', 'h3']:
                                    grouped_content['section_headings'].append(text_content)
                                elif tag in ['h4', 'h5', 'h6']:
                                    grouped_content['sub_headings'].append(text_content)
                                elif tag in ['p'] or (tag == 'div' and len(text_content) > 50):
                                    grouped_content['paragraphs'].append(text_content)
                                elif tag == 'a':
                                    grouped_content['links'].append(text_content)
                                elif tag == 'button':
                                    grouped_content['buttons'].append(text_content)
                                elif tag == 'li':
                                    grouped_content['lists'].append(text_content)
                                elif tag == 'nav':
                                    grouped_content['navigation'].append(text_content)
                                elif tag == 'footer':
                                    grouped_content['footer'].append(text_content)
                                elif tag in ['code', 'pre']:
                                    grouped_content['code'].append(text_content)
                                else:
                                    grouped_content['other'].append(text_content)
                            
                            # Créer UNE entrée par catégorie (au lieu d'une par élément)
                            category_info = {
                                'main_headings': ('📌 Titres Principaux', 'heading', 10),
                                'section_headings': ('📑 Titres de Section', 'heading', 20),
                                'sub_headings': ('📎 Sous-titres', 'heading', 30),
                                'paragraphs': ('📝 Paragraphes', 'text', 40),
                                'links': ('🔗 Liens', 'link', 50),
                                'buttons': ('🔘 Boutons', 'button', 60),
                                'lists': ('📋 Listes', 'list', 70),
                                'navigation': ('🧭 Navigation', 'navigation', 80),
                                'footer': ('📄 Pied de page', 'footer', 90),
                                'code': ('💻 Code', 'code', 100),
                                'other': ('📦 Autres contenus', 'text', 200)
                            }
                            
                            for category_key, contents in grouped_content.items():
                                if contents:  # Seulement si la catégorie contient des éléments
                                    title, content_type, priority = category_info[category_key]
                                    
                                    # Créer une seule entrée groupée
                                    data_item = {
                                        'titre': title,
                                        'type_contenu': content_type,
                                        'categorie': category_key,
                                        'nb_elements': len(contents),
                                        'elements': contents,  # Liste de tous les contenus
                                        'apercu': ' | '.join(contents[:3])[:200] + ('...' if len(contents) > 3 else ''),
                                        'priorite': priority
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type='grouped_content',
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                                    
                            session.add_log(f"[*] Contenus groupés en {len([c for c in grouped_content.values() if c])} catégories", 'info')
                        
                        elif type_name == 'forms':
                            # Récupérer TOUS les formulaires et champs
                            forms = soup.find_all('form')
                            inputs = soup.find_all(['input', 'textarea', 'select', 'option'])
                            session.add_log(f"[*] {len(forms)} formulaires + {len(inputs)} champs trouvés", 'info')
                            
                            # Traiter tous les formulaires
                            for i, form in enumerate(forms):
                                action = form.get('action', '')
                                method = form.get('method', 'GET')
                                form_inputs = form.find_all(['input', 'textarea', 'select'])
                                
                                data_item = {
                                    'titre': f'Formulaire {i+1}',
                                    'action': action,
                                    'method': method,
                                    'nb_champs': len(form_inputs),
                                    'champs': [{'type': inp.get('type', inp.name), 'name': inp.get('name', ''), 'placeholder': inp.get('placeholder', '')} for inp in form_inputs[:20]],
                                    'html': str(form)[:500] + '...' if len(str(form)) > 500 else str(form)
                                }
                                
                                ScrapedData.objects.create(
                                    session=session,
                                    data=data_item,
                                    element_type=type_name,
                                    source_url=url
                                )
                                scraped_data.append(data_item)
                                total_extracted += 1
                            
                            # Traiter tous les champs individuels
                            for i, inp in enumerate(inputs):
                                input_type = inp.get('type', inp.name)
                                name = inp.get('name', '')
                                placeholder = inp.get('placeholder', '')
                                value = inp.get('value', '')
                                
                                if name:  # Seulement si le champ a un nom
                                    data_item = {
                                        'titre': f'Champ {input_type} - {name}',
                                        'type_champ': input_type,
                                        'nom': name,
                                        'placeholder': placeholder,
                                        'valeur_defaut': value,
                                        'requis': inp.has_attr('required'),
                                        'html': str(inp)
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type='form_fields',
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                        
                        elif type_name == 'links':
                            # Récupérer TOUS les liens
                            links = soup.find_all('a', href=True)
                            session.add_log(f"[*] {len(links)} liens trouvés", 'info')
                            
                            links_seen = set()
                            for link in links:
                                href = link.get('href', '')
                                if href and href not in links_seen:
                                    links_seen.add(href)
                                    
                                    # Construire URL absolue
                                    if href.startswith('/'):
                                        from urllib.parse import urljoin
                                        href = urljoin(url, href)
                                    
                                    link_text = link.get_text(strip=True)
                                    link_title = link.get('title', '')
                                    
                                    data_item = {
                                        'titre': link_text[:100] if link_text else 'Lien sans texte',
                                        'url': href,
                                        'texte_lien': link_text,
                                        'titre_lien': link_title,
                                        'type_lien': 'externe' if href.startswith('http') and url not in href else 'interne',
                                        'target': link.get('target', ''),
                                        'rel': link.get('rel', [])
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type=type_name,
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                        
                        elif type_name == 'metadata':
                            # Récupérer TOUTES les métadonnées
                            meta_tags = soup.find_all('meta')
                            link_tags = soup.find_all('link')
                            title_tag = soup.find('title')
                            session.add_log(f"[*] {len(meta_tags)} meta + {len(link_tags)} link tags trouvés", 'info')
                            
                            # Title
                            if title_tag:
                                data_item = {
                                    'titre': 'Title de la page',
                                    'type_meta': 'title',
                                    'contenu': title_tag.get_text(strip=True),
                                    'html': str(title_tag)
                                }
                                ScrapedData.objects.create(
                                    session=session,
                                    data=data_item,
                                    element_type=type_name,
                                    source_url=url
                                )
                                scraped_data.append(data_item)
                                total_extracted += 1
                            
                            # Meta tags
                            for meta in meta_tags:
                                name = meta.get('name', '') or meta.get('property', '') or meta.get('http-equiv', '')
                                content = meta.get('content', '')
                                
                                if name and content:
                                    data_item = {
                                        'titre': f'Meta: {name}',
                                        'type_meta': 'meta',
                                        'nom': name,
                                        'contenu': content,
                                        'html': str(meta)
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type=type_name,
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                            
                            # Link tags (CSS, favicon, etc.)
                            for link in link_tags:
                                rel = link.get('rel', [])
                                href = link.get('href', '')
                                link_type = link.get('type', '')
                                
                                if href:
                                    if href.startswith('/'):
                                        from urllib.parse import urljoin
                                        href = urljoin(url, href)
                                    
                                    data_item = {
                                        'titre': f'Resource: {" ".join(rel) if rel else link_type}',
                                        'type_meta': 'resource',
                                        'url': href,
                                        'relation': rel,
                                        'type_fichier': link_type,
                                        'html': str(link)
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type=type_name,
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                        
                        elif type_name == 'scripts':
                            # Récupérer TOUS les scripts
                            scripts = soup.find_all('script')
                            session.add_log(f"[*] {len(scripts)} scripts trouvés", 'info')
                            
                            for i, script in enumerate(scripts):
                                src = script.get('src', '')
                                script_content = script.get_text(strip=True)
                                script_type = script.get('type', 'text/javascript')
                                
                                if src or script_content:
                                    if src and src.startswith('/'):
                                        from urllib.parse import urljoin
                                        src = urljoin(url, src)
                                    
                                    data_item = {
                                        'titre': f'Script {i+1}',
                                        'url_script': src,
                                        'type_script': script_type,
                                        'taille_code': len(script_content),
                                        'a_src': bool(src),
                                        'a_contenu': bool(script_content),
                                        'contenu_apercu': script_content[:200] + '...' if len(script_content) > 200 else script_content,
                                        'html': str(script)[:300] + '...' if len(str(script)) > 300 else str(script)
                                    }
                                    
                                    ScrapedData.objects.create(
                                        session=session,
                                        data=data_item,
                                        element_type=type_name,
                                        source_url=url
                                    )
                                    scraped_data.append(data_item)
                                    total_extracted += 1
                        
                        elif type_name == 'tables':
                            # Récupérer TOUTES les vraies tables du HTML
                            tables = soup.find_all('table')
                            session.add_log(f"[*] {len(tables)} tables trouvées - EXTRACTION COMPLÈTE", 'info')
                            
                            for i, table in enumerate(tables):  # TOUTES les tables sans limite
                                rows = table.find_all('tr')
                                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                                
                                data_item = {
                                    'titre': f'Tableau {i+1}',
                                    'lignes': len(rows),
                                    'colonnes': len(headers) if headers else len(rows[0].find_all(['td', 'th'])) if rows else 0,
                                    'headers': ', '.join(headers) if headers else 'Aucun header',
                                    'contenu_html': str(table)[:300] + '...' if len(str(table)) > 300 else str(table)
                                }
                                
                                ScrapedData.objects.create(
                                    session=session,
                                    data=data_item,
                                    element_type=type_name,
                                    source_url=url
                                )
                                scraped_data.append(data_item)
                                total_extracted += 1
                
                session.add_log(f"[✓] {len(scraped_data)} éléments extraits", 'success')
            else:
                session.add_log(f"[!] Aucun contenu scrapable trouvé", 'warning')
            
            # Sauvegarder les données extraites dans la configuration
            config = session.configuration or {}
            config['scraped_data'] = scraped_data
            config['total_extracted'] = len(scraped_data)
            session.configuration = config
            session.total_items = len(scraped_data)
            session.success_count = total_extracted
            session.total_items = total_extracted
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()
            
            # Messages de fin détaillés
            total_elements = len(scraped_data)
            types_extracted = set(item.get('type', 'unknown') for item in scraped_data)
            
            if total_elements > 0:
                session.add_log(f"[✓] Scraping terminé avec succès !", 'success')
                session.add_log(f"[✓] {total_elements} éléments extraits", 'success') 
                session.add_log(f"[✓] Types extraits: {', '.join(types_extracted)}", 'success')
            else:
                session.add_log("[!] Aucun élément extrait. Vérifiez la sélection des types ou l'analyse du site.", 'warning')
            
        except Exception as e:
            session.add_log(f"[!] Erreur lors du scraping: {str(e)}", 'error')
            session.mark_failed(str(e))
        
        return Response({
            'session_id': session.id,
            'status': session.status,
            'url': session.url,
            'total_items': session.total_items,
            'message': 'Scraping démarré'
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def export_results(request, session_id):
    """
    Exporte les résultats d'une session de scraping.
    GET /api/results/{session_id}/
    GET /api/results/{session_id}/export/?format=csv|excel|json
    """
    try:
        from django.http import HttpResponse
        import json
        import csv
        import io
        from .models import ScrapingSession
        
        # Récupérer la session - vérifier la propriété si utilisateur authentifié
        session = ScrapingSession.objects.get(id=session_id)
        
        # Vérifier que l'utilisateur a accès à cette session
        if request.user.is_authenticated and session.user != request.user:
            # Si l'utilisateur est authentifié mais ce n'est pas sa session,
            # on autorise quand même pour le développement (à restreindre en prod)
            pass
        
        # Récupérer les données extraites depuis les instances ScrapedData
        scraped_objects = session.scraped_data.all()  # relation ForeignKey
        scraped_data = [obj.data for obj in scraped_objects]
        
        # Si format spécifié dans l'URL, générer le fichier de téléchargement
        export_format = request.GET.get('format', '').lower()
        
        if export_format == 'csv':
            # Export CSV
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.csv"'
            
            if scraped_data:
                writer = csv.DictWriter(response, fieldnames=scraped_data[0].keys())
                writer.writeheader()
                for row in scraped_data:
                    writer.writerow(row)
            else:
                writer = csv.writer(response)
                writer.writerow(['Aucune donnée extraite'])
            
            return response
            
        elif export_format == 'excel':
            # Export Excel (simulé avec CSV pour l'instant)
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.xlsx"'
            
            if scraped_data:
                writer = csv.DictWriter(response, fieldnames=scraped_data[0].keys())
                writer.writeheader()
                for row in scraped_data:
                    writer.writerow(row)
            else:
                writer = csv.writer(response)
                writer.writerow(['Aucune donnée extraite'])
            
            return response
            
        elif export_format == 'json':
            # Export JSON
            response = HttpResponse(content_type='application/json; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.json"'
            
            export_data = {
                'session_id': session.id,
                'url': session.url,
                'status': session.status,
                'scraped_data': scraped_data,
                'statistics': {
                    'total_items': len(scraped_data),
                    'content_types': session.configuration.get('content_types', []),
                    'total_extracted': len(scraped_data)
                },
                'exported_at': timezone.now().isoformat()
            }
            
            json.dump(export_data, response, indent=2, ensure_ascii=False)
            return response
        
        elif export_format == 'xml':
            # Export XML
            import re
            response = HttpResponse(content_type='application/xml; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.xml"'
            
            def sanitize_xml_tag(tag):
                """Nettoie un nom de tag XML pour le rendre valide"""
                # Remplacer les espaces par des underscores
                tag = str(tag).replace(' ', '_')
                # Supprimer les caractères non valides pour XML
                tag = re.sub(r'[^a-zA-Z0-9_-]', '', tag)
                # Le tag ne peut pas commencer par un chiffre
                if tag and tag[0].isdigit():
                    tag = 'item_' + tag
                # Fallback si vide
                return tag or 'field'
            
            def sanitize_xml_value(value):
                """Nettoie une valeur pour XML"""
                if value is None:
                    return ''
                value = str(value)
                # Échapper les caractères XML
                value = value.replace('&', '&amp;')
                value = value.replace('<', '&lt;')
                value = value.replace('>', '&gt;')
                value = value.replace('"', '&quot;')
                value = value.replace("'", '&apos;')
                return value
            
            # Échapper l'URL pour XML
            safe_url = sanitize_xml_value(session.url)
            
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<scraping_session>\n'
            xml_content += f'  <session_id>{session.id}</session_id>\n'
            xml_content += f'  <url>{safe_url}</url>\n'
            xml_content += f'  <status>{session.status}</status>\n'
            xml_content += '  <data>\n'
            
            for item in scraped_data:
                xml_content += '    <item>\n'
                if isinstance(item, dict):
                    for key, value in item.items():
                        safe_key = sanitize_xml_tag(key)
                        # Si la valeur est une liste ou dict, la convertir en string
                        if isinstance(value, (list, dict)):
                            safe_value = sanitize_xml_value(str(value)[:1000])  # Limiter la longueur
                        else:
                            safe_value = sanitize_xml_value(value)
                        xml_content += f'      <{safe_key}>{safe_value}</{safe_key}>\n'
                else:
                    xml_content += f'      <value>{sanitize_xml_value(item)}</value>\n'
                xml_content += '    </item>\n'
            
            xml_content += '  </data>\n</scraping_session>'
            response.write(xml_content)
            return response
        
        elif export_format == 'zip_images':
            # Export ZIP avec toutes les images
            import zipfile
            from urllib.parse import urlparse
            import requests
            
            # Créer un buffer pour le ZIP
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                image_count = 0
                
                for item in scraped_data:
                    category = item.get('category', '')
                    
                    # Chercher les images dans les données
                    if category == 'images':
                        items_list = item.get('items', [])
                        for img_item in items_list:
                            img_url = img_item.get('src') or img_item.get('url', '')
                            if img_url:
                                try:
                                    # Télécharger l'image
                                    img_response = requests.get(img_url, timeout=10)
                                    if img_response.status_code == 200:
                                        # Extraire le nom du fichier
                                        parsed = urlparse(img_url)
                                        filename = parsed.path.split('/')[-1] or f'image_{image_count}.jpg'
                                        if '?' in filename:
                                            filename = filename.split('?')[0]
                                        
                                        zip_file.writestr(f'images/{filename}', img_response.content)
                                        image_count += 1
                                except Exception as e:
                                    # Ignorer les erreurs de téléchargement
                                    pass
                    
                    # Aussi chercher les images dans les items de n'importe quelle catégorie
                    items_list = item.get('items', [])
                    for sub_item in items_list:
                        if isinstance(sub_item, dict):
                            img_url = sub_item.get('src', '')
                            if img_url and ('.jpg' in img_url or '.png' in img_url or '.gif' in img_url or '.webp' in img_url):
                                try:
                                    img_response = requests.get(img_url, timeout=10)
                                    if img_response.status_code == 200:
                                        parsed = urlparse(img_url)
                                        filename = parsed.path.split('/')[-1] or f'image_{image_count}.jpg'
                                        if '?' in filename:
                                            filename = filename.split('?')[0]
                                        
                                        zip_file.writestr(f'images/{filename}', img_response.content)
                                        image_count += 1
                                except:
                                    pass
                
                # Ajouter un fichier index.json avec les métadonnées
                index_data = {
                    'session_id': session.id,
                    'url': session.url,
                    'total_images': image_count,
                    'exported_at': timezone.now().isoformat()
                }
                zip_file.writestr('index.json', json.dumps(index_data, indent=2))
            
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="images_session_{session_id}.zip"'
            return response
        
        # Si pas de format, retourner les données JSON normales
        export_data = {
            'session_id': session.id,
            'url': session.url,
            'status': session.status,
            'scraped_data': scraped_data,
            'statistics': {
                'total_items': len(scraped_data),
                'content_types': session.configuration.get('content_types', []),
                'total_extracted': len(scraped_data),
                'pages_crawled': session.total_items or 0
            },
            'metadata': {
                'created_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'configuration': session.configuration
            }
        }
        
        return Response(export_data)
        
    except ScrapingSession.DoesNotExist:
        return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request):
        """
        Lance une nouvelle session de scraping.
        POST /api/scraping/
        Body: { "url": "https://example.com", "configuration": {...} }
        """
        serializer = CreateScrapingSessionSerializer(data=request.data)
        if serializer.is_valid():
            # Crée la session
            session = serializer.save(user=request.user, status='pending')
            
            # Lance le scraping en background (simplifié ici)
            try:
                session.status = 'in_progress'
                session.save()
                
                if Scraper:
                    scraper = Scraper()
                    # Ici tu peux appeler ton scraper
                    # result = scraper.scrape(session.url, session.configuration)
                    # Pour l'instant on simule
                    pass
                
                session.status = 'completed'
                session.completed_at = timezone.now()
                session.total_items = 10
                session.success_count = 10
                session.save()
                
            except Exception as e:
                session.mark_failed(str(e))
            
            return Response(
                ScrapingSessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Annule une session de scraping en cours.
        POST /api/scraping/{id}/cancel/
        """
        session = self.get_object()
        if session.status in ['pending', 'in_progress']:
            session.status = 'failed'
            session.error_message = 'Annulé par l\'utilisateur'
            session.completed_at = timezone.now()
            session.save()
            return Response({'message': 'Session annulée'}, status=status.HTTP_200_OK)
        return Response({'error': 'Session déjà terminée'}, status=status.HTTP_400_BAD_REQUEST)


class ResultsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour récupérer les résultats de scraping.
    """
    serializer_class = ScrapedDataSerializer
    permission_classes = [AllowAny]  # Changé pour permettre l'export sans auth en dev
    
    def get_queryset(self):
        """Retourne uniquement les données des sessions de l'utilisateur."""
        if self.request.user.is_authenticated:
            return ScrapedData.objects.filter(session__user=self.request.user)
        return ScrapedData.objects.all()  # En dev, permettre l'accès
    
    def retrieve(self, request, pk=None):
        """
        Récupère les résultats d'une session de scraping par son ID.
        GET /api/results/{session_id}/
        Note: pk ici représente le session_id, pas le ScrapedData id
        """
        try:
            session = ScrapingSession.objects.get(id=pk)
            
            # Récupérer les données extraites
            scraped_objects = session.scraped_data.all()
            scraped_data = [obj.data for obj in scraped_objects]
            
            return Response({
                'session_id': session.id,
                'url': session.url,
                'status': session.status,
                'scraped_data': scraped_data,
                'statistics': {
                    'total_items': len(scraped_data),
                    'content_types': session.configuration.get('content_types', []),
                    'total_extracted': len(scraped_data),
                    'pages_crawled': session.total_items or 0
                },
                'metadata': {
                    'created_at': session.started_at.isoformat() if session.started_at else None,
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                    'configuration': session.configuration
                }
            })
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='export')
    def export(self, request, pk=None):
        """
        Exporte les résultats d'une session de scraping.
        GET /api/results/{session_id}/export/?type=csv|excel|json|xml|zip_images&limit=100&item_ids=1,2,3
        """
        import re
        import zipfile
        from urllib.parse import urlparse
        import requests as req_lib
        
        session_id = pk
        # Note: 'format' est réservé par DRF, on utilise 'type' à la place
        export_format = request.GET.get('type', request.GET.get('format', 'json')).lower()
        
        # Paramètres de filtrage
        limit = request.GET.get('limit', None)
        item_ids = request.GET.get('item_ids', None)
        
        try:
            session = ScrapingSession.objects.get(id=session_id)
            
            # Récupérer les données extraites
            scraped_objects = session.scraped_data.all()
            
            # Filtrer par IDs si spécifiés
            if item_ids:
                try:
                    ids_list = [int(id.strip()) for id in item_ids.split(',')]
                    scraped_objects = scraped_objects.filter(id__in=ids_list)
                except ValueError:
                    pass  # Ignorer les IDs invalides
            
            # Limiter le nombre si spécifié
            if limit:
                try:
                    limit_int = int(limit)
                    scraped_objects = scraped_objects[:limit_int]
                except ValueError:
                    pass  # Ignorer les limites invalides
            
            scraped_data = [obj.data for obj in scraped_objects]
            
            if export_format == 'csv':
                # Export CSV
                response = HttpResponse(content_type='text/csv; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.csv"'
                
                if scraped_data:
                    # Aplatir les données pour CSV
                    flat_data = []
                    all_fieldnames = set()
                    
                    for item in scraped_data:
                        if isinstance(item, dict):
                            flat_item = {}
                            for key, value in item.items():
                                if isinstance(value, (list, dict)):
                                    flat_item[key] = str(value)[:2000]  # Augmenté pour avoir plus de données
                                else:
                                    flat_item[key] = value
                                all_fieldnames.add(key)
                            flat_data.append(flat_item)
                    
                    if flat_data:
                        # Utiliser tous les fieldnames de toutes les lignes
                        fieldnames = list(all_fieldnames)
                        writer = csv.DictWriter(response, fieldnames=fieldnames, extrasaction='ignore')
                        writer.writeheader()
                        for row in flat_data:
                            # Remplir les champs manquants avec ''
                            complete_row = {fn: row.get(fn, '') for fn in fieldnames}
                            writer.writerow(complete_row)
                else:
                    writer = csv.writer(response)
                    writer.writerow(['Aucune donnée extraite'])
                
                return response
                
            elif export_format == 'excel':
                # Export Excel (CSV avec extension xlsx)
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.xlsx"'
                
                if scraped_data:
                    flat_data = []
                    all_fieldnames = set()
                    
                    for item in scraped_data:
                        if isinstance(item, dict):
                            flat_item = {}
                            for key, value in item.items():
                                if isinstance(value, (list, dict)):
                                    flat_item[key] = str(value)[:2000]
                                else:
                                    flat_item[key] = value
                                all_fieldnames.add(key)
                            flat_data.append(flat_item)
                    
                    if flat_data:
                        fieldnames = list(all_fieldnames)
                        writer = csv.DictWriter(response, fieldnames=fieldnames, extrasaction='ignore')
                        writer.writeheader()
                        for row in flat_data:
                            complete_row = {fn: row.get(fn, '') for fn in fieldnames}
                            writer.writerow(complete_row)
                
                return response
                
            elif export_format == 'json':
                # Export JSON
                response = HttpResponse(content_type='application/json; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.json"'
                
                export_data = {
                    'session_id': session.id,
                    'url': session.url,
                    'status': session.status,
                    'scraped_data': scraped_data,
                    'exported_at': timezone.now().isoformat()
                }
                
                json.dump(export_data, response, indent=2, ensure_ascii=False)
                return response
            
            elif export_format == 'xml':
                # Export XML
                response = HttpResponse(content_type='application/xml; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="scraping_session_{session_id}.xml"'
                
                def sanitize_xml_tag(tag):
                    tag = str(tag).replace(' ', '_')
                    tag = re.sub(r'[^a-zA-Z0-9_-]', '', tag)
                    if tag and tag[0].isdigit():
                        tag = 'item_' + tag
                    return tag or 'field'
                
                def sanitize_xml_value(value):
                    if value is None:
                        return ''
                    value = str(value)
                    value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    return value
                
                safe_url = sanitize_xml_value(session.url)
                
                xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<scraping_session>\n'
                xml_content += f'  <session_id>{session.id}</session_id>\n'
                xml_content += f'  <url>{safe_url}</url>\n'
                xml_content += f'  <status>{session.status}</status>\n'
                xml_content += '  <data>\n'
                
                for item in scraped_data:
                    xml_content += '    <item>\n'
                    if isinstance(item, dict):
                        for key, value in item.items():
                            safe_key = sanitize_xml_tag(key)
                            if isinstance(value, (list, dict)):
                                safe_value = sanitize_xml_value(str(value)[:1000])
                            else:
                                safe_value = sanitize_xml_value(value)
                            xml_content += f'      <{safe_key}>{safe_value}</{safe_key}>\n'
                    xml_content += '    </item>\n'
                
                xml_content += '  </data>\n</scraping_session>'
                response.write(xml_content)
                return response
            
            elif export_format == 'zip_images':
                # Export ZIP avec toutes les images
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    image_count = 0
                    image_urls = []
                    
                    for item in scraped_data:
                        if not isinstance(item, dict):
                            continue
                        
                        # Vérifier si c'est un élément image (type_media=image)
                        type_media = item.get('type_media', '')
                        titre = item.get('titre', '')
                        
                        # Récupérer les éléments (images sont dans 'elements')
                        elements = item.get('elements', [])
                        
                        if type_media == 'image' or 'image' in titre.lower():
                            for sub_item in elements:
                                if isinstance(sub_item, dict):
                                    img_url = sub_item.get('src', '') or sub_item.get('url', '')
                                    if img_url and img_url not in image_urls:
                                        image_urls.append(img_url)
                    
                    # Télécharger chaque image unique
                    for img_url in image_urls:
                        # Ignorer les data URLs (base64)
                        if img_url.startswith('data:'):
                            continue
                            
                        try:
                            img_response = req_lib.get(img_url, timeout=15, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            })
                            if img_response.status_code == 200:
                                parsed = urlparse(img_url)
                                filename = parsed.path.split('/')[-1] or f'image_{image_count}.jpg'
                                if '?' in filename:
                                    filename = filename.split('?')[0]
                                
                                # Éviter les doublons de nom
                                original_filename = filename
                                counter = 1
                                while filename in [name for name in zip_file.namelist()]:
                                    name, ext = original_filename.rsplit('.', 1) if '.' in original_filename else (original_filename, 'jpg')
                                    filename = f'{name}_{counter}.{ext}'
                                    counter += 1
                                
                                zip_file.writestr(f'images/{filename}', img_response.content)
                                image_count += 1
                        except Exception as e:
                            # Ignorer les erreurs de téléchargement
                            pass
                    
                    # Ajouter un fichier index.json avec la liste des URLs
                    index_data = {
                        'session_id': session.id,
                        'url': session.url,
                        'total_images': image_count,
                        'image_urls': image_urls,
                        'exported_at': timezone.now().isoformat()
                    }
                    zip_file.writestr('index.json', json.dumps(index_data, indent=2, ensure_ascii=False))
                
                zip_buffer.seek(0)
                response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="images_session_{session_id}.zip"'
                return response
            
            else:
                # Format non supporté, retourner JSON par défaut
                return Response({
                    'error': f'Format non supporté: {export_format}',
                    'formats_disponibles': ['csv', 'excel', 'json', 'xml', 'zip_images']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """
        Récupère tous les résultats d'une session.
        GET /api/results/by_session/?session_id=123
        """
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'session_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = ScrapingSession.objects.get(id=session_id, user=request.user)
            data = ScrapedData.objects.filter(session=session)
            serializer = self.get_serializer(data, many=True)
            return Response({
                'session': ScrapingSessionSerializer(session).data,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except ScrapingSession.DoesNotExist:
            return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)


class ReportsViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les rapports et statistiques.
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne uniquement les rapports de l'utilisateur."""
        return Report.objects.filter(user=self.request.user)
    
    def list(self, request):
        """
        Retourne les statistiques et l'historique des sessions.
        GET /api/reports/?period=30+jours
        """
        from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Sum
        from django.db.models.functions import TruncDate
        from datetime import datetime, timedelta
        
        period = request.GET.get('period', '30 jours')
        user = request.user
        
        # Déterminer la période
        if '7' in period:
            days = 7
        elif '90' in period:
            days = 90
        elif 'tout' in period.lower() or 'all' in period.lower():
            days = 365 * 10  # 10 ans
        else:
            days = 30
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Filtrer les sessions de la période
        sessions = ScrapingSession.objects.filter(
            user=user,
            started_at__gte=start_date
        ).order_by('-started_at')
        
        # Statistiques
        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        failed_sessions = sessions.filter(status='failed').count()
        
        # Éléments extraits
        total_elements = ScrapedData.objects.filter(
            session__user=user,
            session__started_at__gte=start_date
        ).count()
        
        # Taux de succès
        if total_sessions > 0:
            success_rate = round((completed_sessions / total_sessions) * 100, 1)
            error_rate = round((failed_sessions / total_sessions) * 100, 1)
        else:
            success_rate = 0
            error_rate = 0
        
        # Temps moyen
        avg_duration = sessions.filter(
            status='completed',
            completed_at__isnull=False
        ).annotate(
            duration=ExpressionWrapper(
                F('completed_at') - F('started_at'),
                output_field=fields.DurationField()
            )
        ).aggregate(avg=Avg('duration'))['avg']
        
        if avg_duration:
            total_seconds = int(avg_duration.total_seconds())
            if total_seconds < 60:
                avg_time = f"{total_seconds}s"
            else:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                avg_time = f"{minutes}m {seconds}s"
        else:
            avg_time = "0s"
        
        # Données pour le graphique (par jour)
        activity_data = sessions.annotate(
            day=TruncDate('started_at')
        ).values('day').annotate(
            count=Count('id'),
            elements=Sum('total_items')
        ).order_by('day')
        
        chart_labels = []
        chart_sessions = []
        chart_elements = []
        
        for entry in activity_data:
            if entry['day']:
                chart_labels.append(entry['day'].strftime('%d/%m'))
                chart_sessions.append(entry['count'] or 0)
                chart_elements.append(entry['elements'] or 0)
        
        # Liste des sessions
        sessions_list = []
        for session in sessions[:50]:  # Limiter à 50
            duration = None
            if session.completed_at and session.started_at:
                duration_delta = session.completed_at - session.started_at
                duration_secs = int(duration_delta.total_seconds())
                if duration_secs < 60:
                    duration = f"{duration_secs}s"
                else:
                    duration = f"{duration_secs // 60}m {duration_secs % 60}s"
            
            sessions_list.append({
                'id': session.id,
                'url': session.url,
                'status': session.status,
                'total_items': session.total_items or 0,
                'duration': duration or '-',
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            })
        
        return Response({
            'stats': {
                'total_sessions': total_sessions,
                'total_elements': total_elements,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'avg_time': avg_time,
                'completed_sessions': completed_sessions,
                'failed_sessions': failed_sessions,
            },
            'chart': {
                'labels': chart_labels,
                'sessions': chart_sessions,
                'elements': chart_elements,
            },
            'sessions': sessions_list,
            'reports': []  # Les rapports générés
        })
    
    def create(self, request):
        """
        Crée un nouveau rapport.
        POST /api/reports/
        Body: { "session": 123, "title": "Mon rapport", "format": "pdf", "content": {...} }
        """
        serializer = CreateReportSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifie que la session appartient à l'utilisateur
            session_id = serializer.validated_data['session'].id
            try:
                session = ScrapingSession.objects.get(id=session_id, user=request.user)
                report = serializer.save(user=request.user)
                return Response(
                    ReportSerializer(report).data,
                    status=status.HTTP_201_CREATED
                )
            except ScrapingSession.DoesNotExist:
                return Response({'error': 'Session non trouvée'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Télécharge un rapport.
        GET /api/reports/{id}/download/
        """
        report = self.get_object()
        # Ici tu peux implémenter la logique de téléchargement
        return Response({
            'message': 'Téléchargement du rapport',
            'report': ReportSerializer(report).data,
            'download_url': f'/media/reports/{report.id}.{report.format}'
        }, status=status.HTTP_200_OK)


class SettingsViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les paramètres utilisateur (API keys et webhooks).
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'post'], url_path='api-keys')
    def api_keys(self, request):
        """
        GET: Liste toutes les clés API de l'utilisateur
        POST: Crée une nouvelle clé API
        """
        if request.method == 'GET':
            keys = ApiKey.objects.filter(user=request.user)
            serializer = ApiKeySerializer(keys, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CreateApiKeySerializer(data=request.data)
            if serializer.is_valid():
                api_key = serializer.save(user=request.user)
                return Response(
                    ApiKeySerializer(api_key).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='api-keys')
    def delete_api_key(self, request, pk=None):
        """
        DELETE: Supprime une clé API
        """
        try:
            api_key = ApiKey.objects.get(id=pk, user=request.user)
            api_key.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ApiKey.DoesNotExist:
            return Response({'error': 'Clé API non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get', 'post'], url_path='webhooks')
    def webhooks(self, request):
        """
        GET: Liste tous les webhooks de l'utilisateur
        POST: Crée un nouveau webhook
        """
        if request.method == 'GET':
            webhooks = Webhook.objects.filter(user=request.user)
            serializer = WebhookSerializer(webhooks, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CreateWebhookSerializer(data=request.data)
            if serializer.is_valid():
                webhook = serializer.save(user=request.user)
                return Response(
                    WebhookSerializer(webhook).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='webhooks')
    def delete_webhook(self, request, pk=None):
        """
        DELETE: Supprime un webhook
        """
        try:
            webhook = Webhook.objects.get(id=pk, user=request.user)
            webhook.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Webhook.DoesNotExist:
            return Response({'error': 'Webhook non trouvé'}, status=status.HTTP_404_NOT_FOUND)


class SettingsViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les paramètres utilisateur (API keys, webhooks).
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get', 'post'], url_path='api-keys')
    def api_keys(self, request):
        """
        GET: Liste toutes les clés API de l'utilisateur
        POST: Crée une nouvelle clé API
        """
        if request.method == 'GET':
            keys = ApiKey.objects.filter(user=request.user)
            serializer = ApiKeySerializer(keys, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CreateApiKeySerializer(data=request.data)
            if serializer.is_valid():
                api_key = serializer.save(user=request.user)
                # Retourner la clé complète une seule fois
                return Response({
                    'id': api_key.id,
                    'name': api_key.name,
                    'key': api_key.key,  # Clé complète, affichée une seule fois
                    'key_prefix': api_key.key_prefix,
                    'created_at': api_key.created_at
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], url_path='api-keys/(?P<key_id>[^/.]+)')
    def delete_api_key(self, request, key_id=None):
        """
        DELETE: Supprime une clé API
        """
        try:
            api_key = ApiKey.objects.get(id=key_id, user=request.user)
            api_key.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ApiKey.DoesNotExist:
            return Response({'error': 'Clé API non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get', 'post'], url_path='webhooks')
    def webhooks(self, request):
        """
        GET: Liste tous les webhooks de l'utilisateur
        POST: Crée un nouveau webhook
        """
        if request.method == 'GET':
            webhooks = Webhook.objects.filter(user=request.user)
            serializer = WebhookSerializer(webhooks, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CreateWebhookSerializer(data=request.data)
            if serializer.is_valid():
                webhook = serializer.save(user=request.user)
                return Response(WebhookSerializer(webhook).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'], url_path='webhooks/(?P<webhook_id>[^/.]+)')
    def delete_webhook(self, request, webhook_id=None):
        """
        DELETE: Supprime un webhook
        """
        try:
            webhook = Webhook.objects.get(id=webhook_id, user=request.user)
            webhook.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Webhook.DoesNotExist:
            return Response({'error': 'Webhook non trouvé'}, status=status.HTTP_404_NOT_FOUND)
