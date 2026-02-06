# backend/api/serializers.py
# Serializers Django REST Framework pour tous les modèles
# Convertit les modèles Django en JSON et vice-versa
# RELEVANT FILES: api/models.py, api/views.py, config/settings.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, ScrapingSession, ScrapedData, Report, ApiKey, Webhook
import secrets


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle User.
    Utilisé pour l'affichage des informations utilisateur.
    """
    name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'name', 'phone', 'company', 'created_at', 'is_2fa_enabled', 'avatar_url']
        read_only_fields = ['id', 'created_at']
    
    def get_name(self, obj):
        """Retourne le nom complet ou le username si vide."""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription d'un nouvel utilisateur.
    Gère la création sécurisée du mot de passe.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone', 'company']
    
    def validate(self, attrs):
        """Vérifie que les deux mots de passe correspondent et l'unicité de l'email."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": ["Un utilisateur avec cet email existe déjà."]})
            
        return attrs
    
    def create(self, validated_data):
        """Crée un nouvel utilisateur avec mot de passe hashé."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            company=validated_data.get('company', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion.
    Vérifie les credentials et retourne le token.
    Accepte email ou username.
    """
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Authentifie l'utilisateur."""
        email = attrs.get('email')
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Si email fourni, on récupère le username
        if email and not username:
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                raise serializers.ValidationError("Identifiants invalides.")
        
        if not username:
            raise serializers.ValidationError("Email ou nom d'utilisateur requis.")
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError("Identifiants invalides.")
        
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")
        
        attrs['user'] = user
        return attrs


class ScrapingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer pour ScrapingSession.
    Affiche les informations complètes d'une session de scraping.
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ScrapingSession
        fields = [
            'id', 'user', 'user_name', 'url', 'status', 'configuration',
            'started_at', 'completed_at', 'error_message',
            'total_items', 'success_count', 'error_count'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'completed_at', 'total_items', 'success_count', 'error_count']


class CreateScrapingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer une nouvelle session de scraping.
    Simplifié pour accepter uniquement l'URL et la config.
    """
    class Meta:
        model = ScrapingSession
        fields = ['url', 'configuration']


class ScrapedDataSerializer(serializers.ModelSerializer):
    """
    Serializer pour ScrapedData.
    Affiche les données extraites.
    """
    class Meta:
        model = ScrapedData
        fields = ['id', 'session', 'data', 'extracted_at', 'element_type', 'source_url']
        read_only_fields = ['id', 'extracted_at']


class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer pour Report.
    Affiche les rapports générés.
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    session_url = serializers.URLField(source='session.url', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'session', 'session_url', 'user', 'user_name',
            'title', 'format', 'content', 'file_path',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CreateReportSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer un nouveau rapport.
    """
    class Meta:
        model = Report
        fields = ['session', 'title', 'format', 'content']


class ApiKeySerializer(serializers.ModelSerializer):
    """
    Serializer pour ApiKey.
    """
    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'key', 'key_prefix', 'is_active', 'created_at', 'last_used']
        read_only_fields = ['id', 'key', 'key_prefix', 'created_at', 'last_used']


class CreateApiKeySerializer(serializers.ModelSerializer):
    """
    Serializer pour créer une nouvelle clé API.
    """
    class Meta:
        model = ApiKey
        fields = ['name']
    
    def create(self, validated_data):
        # Générer une clé aléatoire sécurisée
        key = secrets.token_urlsafe(32)
        validated_data['key'] = key
        validated_data['key_prefix'] = key[:8]
        return super().create(validated_data)


class WebhookSerializer(serializers.ModelSerializer):
    """
    Serializer pour Webhook.
    """
    class Meta:
        model = Webhook
        fields = ['id', 'url', 'events', 'is_active', 'created_at', 'last_triggered', 'success_count', 'failure_count']
        read_only_fields = ['id', 'created_at', 'last_triggered', 'success_count', 'failure_count']


class CreateWebhookSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer un nouveau webhook.
    """
    class Meta:
        model = Webhook
        fields = ['url', 'events']
