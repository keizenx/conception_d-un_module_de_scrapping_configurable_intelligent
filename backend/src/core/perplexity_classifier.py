# backend/src/core/perplexity_classifier.py
# Service d'identification intelligente des types de contenu via Perplexity AI
# Remplace la détection générique par une analyse IA précise
# RELEVANT FILES: analyzer.py, views.py, scraper.py

import httpx
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class PerplexityClassifier:
    """
    Utilise Perplexity AI pour identifier intelligemment les types de contenu d'un site web.
    Analyse le contenu réel et la structure pour déterminer la nature du site.
    """
    
    def __init__(self, api_key: str = None):
        # Utiliser la clé depuis .env ou celle fournie en paramètre
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY', '')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def classify_content(
        self, 
        url: str, 
        page_title: str = "", 
        sample_text: str = "",
        detected_fields: List[str] = None,
        html_content: str = ""
    ) -> Dict:
        """
        Identifie le type de contenu d'un site.
        Stratégie: 1) Métadonnées (gratuit), 2) Perplexity AI, 3) Fallback
        
        Args:
            url: URL du site à analyser
            page_title: Titre de la page
            sample_text: Extrait du contenu de la page
            detected_fields: Champs détectés (price, date, image, etc.)
            html_content: Contenu HTML complet pour extraction de métadonnées
        
        Returns:
            {
                'type': 'ecommerce' | 'blog' | 'news' | 'education' | 'corporate' | 'portfolio' | 'forum',
                'title': 'Nom descriptif du type de contenu',
                'icon': 'Emoji approprié',
                'confidence': 0.0-1.0,
                'description': 'Description détaillée'
            }
        """
        
        # STRATÉGIE 1: Analyser les métadonnées (OpenGraph, Schema.org) - 100% GRATUIT
        if html_content:
            try:
                from .metadata_classifier import MetadataClassifier
                meta_classifier = MetadataClassifier()
                meta_result = meta_classifier.classify_from_metadata(html_content, url)
                
                if meta_result and meta_result.get('confidence', 0) >= 0.7:
                    print(f"[✓] Classification via métadonnées: {meta_result['type']} (confiance: {meta_result['confidence']:.0%})")
                    return meta_result
            except Exception as e:
                print(f"[!] Erreur métadonnées: {e}")
        
        # STRATÉGIE 2: Utiliser Perplexity AI (payant mais précis)
        # Note: Désactivé pour économiser - utilise directement le fallback
        # Pour activer, décommenter le bloc ci-dessous et commenter la ligne suivante
        
        # STRATÉGIE 3: Fallback avec analyse de mots-clés (100% gratuit et rapide)
        print(f"[*] Utilisation du fallback classifier basé sur les mots-clés")
        return self._fallback_classification(detected_fields, url, page_title, sample_text)
        
        # Code Perplexity désactivé - décommenter ce qui suit pour activer
        # Préparer le contexte pour Perplexity
        # context = f"""
        # Analyse ce site web et identifie son type de contenu principal:
        # 
        # URL: {url}
        # Titre: {page_title}
        # Extrait de contenu: {sample_text[:500] if sample_text else "N/A"}
        # Champs détectés: {', '.join(detected_fields) if detected_fields else "Aucun"}
        # 
        # Retourne UNIQUEMENT un JSON avec cette structure exacte (sans markdown, sans balises):
        # {{
        #     "type": "un seul mot parmi: ecommerce, blog, news, education, corporate, portfolio, forum, gallery, documentation, social",
        #     "title": "Nom descriptif court (2-4 mots)",
        #     "description": "Description en une phrase",
        #     "confidence": score entre 0 et 1
        # }}
        # """
        # 
        # try:
        #     payload = {
        #         "model": "llama-3.1-sonar-small-128k-online",
        #         "messages": [
        #             {
        #                 "role": "user",
        #                 "content": context
        #             }
        #         ],
        #         "temperature": 0.2,
        #         "max_tokens": 150,
        #         "return_citations": False,
        #         "return_images": False
        #     }
        #     
        #     with httpx.Client(timeout=15.0) as client:
        #         response = client.post(
        #             self.base_url,
        #             headers=self.headers,
        #             json=payload
        #         )
        #         
        #         # Afficher l'erreur si status != 200
        #         if response.status_code != 200:
        #             print(f"[!] Perplexity Error {response.status_code}: {response.text}")
        #             return self._fallback_classification(detected_fields, url, page_title, sample_text)
        #         
        #         response.raise_for_status()
        #         
        #         result = response.json()
        #         content = result['choices'][0]['message']['content']
        #         
        #         # Nettoyer le contenu (enlever markdown si présent)
        #         content = content.strip()
        #         if content.startswith('```'):
        #             # Enlever les balises markdown
        #             content = content.split('```')[1]
        #             if content.startswith('json'):
        #                 content = content[4:]
        #             content = content.strip()
        #         
        #         # Parser le JSON
        #         classification = json.loads(content)
        #         
        #         # Ajouter l'icône appropriée
        #         classification['icon'] = self._get_icon_for_type(classification.get('type', 'corporate'))
        #         
        #         return classification
        #         
        # except Exception as e:
        #     print(f"[!] Erreur Perplexity: {e}")
        #     if hasattr(e, 'response'):
        #         try:
        #             error_detail = e.response.json()
        #             print(f"[!] Détail erreur: {error_detail}")
        #         except:
        #             pass
        #     # Fallback: classification basique
        #     return self._fallback_classification(detected_fields, url, page_title, sample_text)
    
    def _get_icon_for_type(self, content_type: str) -> str:
        """Retourne l'icône Material Icon appropriée pour chaque type."""
        icons = {
            'ecommerce': 'shopping_cart',
            'blog': 'article',
            'news': 'newspaper',
            'education': 'school',
            'corporate': 'business',
            'portfolio': 'photo_library',
            'forum': 'forum',
            'gallery': 'collections',
            'documentation': 'description',
            'social': 'people',
            'restaurant': 'restaurant',
            'health': 'local_hospital',
            'real_estate': 'home',
            'job': 'work',
            'travel': 'flight',
            'entertainment': 'movie',
            'government': 'account_balance',
            'nonprofit': 'volunteer_activism',
            'sports': 'sports_soccer',
            'finance': 'account_balance_wallet',
            'automotive': 'directions_car',
            'fashion': 'checkroom',
            'beauty': 'spa',
            'gaming': 'sports_esports'
        }
        return icons.get(content_type, 'public')
    
    def _fallback_classification(self, detected_fields: List[str] = None, url: str = '', page_title: str = '', sample_text: str = '') -> Dict:
        """Classification de secours si Perplexity échoue."""
        
        # Analyser l'URL et le contenu pour une meilleure classification
        url_lower = url.lower()
        title_lower = page_title.lower()
        text_lower = sample_text.lower() if sample_text else ''
        content_to_check = f"{url_lower} {title_lower} {text_lower[:2000]}"
        
        # Vérifier l'extension de domaine d'abord (indicateur fort)
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Extensions spécifiques
        if any(domain.endswith(ext) for ext in ['.edu', '.ac.uk', '.edu.au', '.edu.cn', '.edu.ci']):
            return {
                'type': 'education',
                'title': 'Établissement Éducatif',
                'icon': 'school',
                'confidence': 0.95,
                'description': 'Institution académique officielle'
            }
        
        # Vérifier les noms de domaine éducatifs connus (Côte d'Ivoire)
        educational_domains = ['iit.ci', 'inphb.ci', 'univ', 'university', 'college', 'school', 'academy', 'institute', 'esatic']
        if any(edu_name in domain for edu_name in educational_domains):
            # Pour les sites éducatifs, retourner directement sans autre vérification
            # Car même les pages de programmes peuvent contenir des prix (frais de scolarité)
            return {
                'type': 'education',
                'title': 'Établissement Éducatif',
                'icon': 'school',
                'confidence': 0.92,
                'description': 'École, université ou centre de formation'
            }
        elif any(domain.endswith(ext) for ext in ['.gov', '.gouv.fr', '.gov.uk']):
            return {
                'type': 'government',
                'title': 'Site Gouvernemental',
                'icon': 'account_balance',
                'confidence': 0.95,
                'description': 'Site officiel du gouvernement'
            }
        elif any(domain.endswith(ext) for ext in ['.org', '.ong']):
            if any(kw in content_to_check for kw in ['donation', 'don', 'charité', 'charity', 'association', 'ong', 'ngo']):
                return {
                    'type': 'nonprofit',
                    'title': 'Organisation à But Non Lucratif',
                    'icon': 'volunteer_activism',
                    'confidence': 0.85,
                    'description': 'Organisation caritative ou associative'
                }
        
        # Mots-clés détaillés pour chaque catégorie
        keywords = {
            'education': {
                'keywords': [
                    'université', 'university', 'école', 'school', 'college', 'formation', 'education',
                    'cours', 'course', 'étudiant', 'student', 'campus', 'académie', 'academy',
                    'institut', 'institute', 'apprentissage', 'learning', 'diplôme', 'degree',
                    'bachelor', 'master', 'programme', 'program', 'enseignement', 'teaching',
                    'professeur', 'professor', 'classe', 'class', 'licence', 'doctorat', 'phd',
                    'admissions', 'inscription', 'scolarité', 'tuition', 'faculté', 'faculty'
                ],
                'weight': 1.5,  # Poids plus élevé pour l'éducation
                'icon': 'school',
                'title': 'Établissement Éducatif',
                'description': 'École, université ou centre de formation'
            },
            'ecommerce': {
                'keywords': [
                    'shop', 'store', 'boutique', 'acheter', 'buy', 'panier', 'cart', 'checkout',
                    'produit', 'product', 'prix', 'price', 'vente', 'sale', 'promo', 'discount',
                    'livraison', 'shipping', 'delivery', 'commander', 'order', 'paiement', 'payment',
                    'add to cart', 'ajouter au panier', 'stock', 'disponible', 'available',
                    'catalogue', 'catalog', 'catégorie', 'category'
                ],
                'weight': 1.0,
                'icon': 'shopping_cart',
                'title': 'E-commerce',
                'description': 'Site de vente en ligne'
            },
            'news': {
                'keywords': [
                    'actualité', 'actualités', 'news', 'journal', 'newspaper', 'presse', 'press',
                    'information', 'média', 'media', 'reportage', 'report', 'édition', 'edition',
                    'journaliste', 'journalist', 'rédaction', 'breaking', 'dernière heure',
                    'direct', 'live', 'vidéo', 'video', 'politique', 'politique', 'économie', 'economy'
                ],
                'weight': 1.2,
                'icon': 'newspaper',
                'title': 'Site d\'Actualités',
                'description': 'Média d\'information et actualités'
            },
            'blog': {
                'keywords': [
                    'blog', 'article', 'post', 'publication', 'auteur', 'author', 'écrit par', 'written by',
                    'commentaire', 'comment', 'partager', 'share', 'suivre', 'follow',
                    'abonner', 'subscribe', 'newsletter', 'publié', 'published', 'tags', 'catégories'
                ],
                'weight': 1.0,
                'icon': 'article',
                'title': 'Blog',
                'description': 'Blog personnel ou professionnel'
            },
            'portfolio': {
                'keywords': [
                    'portfolio', 'projets', 'projects', 'réalisations', 'works', 'créations',
                    'galerie', 'gallery', 'designer', 'développeur', 'developer', 'artist',
                    'photographe', 'photographer', 'créatif', 'creative', 'showcase'
                ],
                'weight': 1.0,
                'icon': 'photo_library',
                'title': 'Portfolio',
                'description': 'Portfolio professionnel ou artistique'
            },
            'forum': {
                'keywords': [
                    'forum', 'discussion', 'topic', 'thread', 'post', 'membre', 'member',
                    'répondre', 'reply', 'community', 'communauté', 'messages', 'sujet',
                    'fil de discussion', 'modérateur', 'moderator', 'upvote', 'vote'
                ],
                'weight': 1.1,
                'icon': 'forum',
                'title': 'Forum',
                'description': 'Forum de discussion communautaire'
            },
            'social': {
                'keywords': [
                    'social', 'réseau', 'network', 'profil', 'profile', 'ami', 'friend',
                    'follower', 'suiveur', 'like', 'j\'aime', 'partager', 'share', 'timeline',
                    'feed', 'fil', 'message privé', 'dm', 'notification', 'hashtag'
                ],
                'weight': 1.0,
                'icon': 'people',
                'title': 'Réseau Social',
                'description': 'Plateforme de réseau social'
            },
            'documentation': {
                'keywords': [
                    'documentation', 'docs', 'guide', 'tutorial', 'api', 'référence', 'reference',
                    'manuel', 'manual', 'getting started', 'quickstart', 'installation',
                    'configuration', 'exemples', 'examples', 'faq'
                ],
                'weight': 1.0,
                'icon': 'description',
                'title': 'Documentation',
                'description': 'Documentation technique ou guide'
            },
            'restaurant': {
                'keywords': [
                    'restaurant', 'menu', 'carte', 'réservation', 'reservation', 'booking',
                    'cuisine', 'chef', 'plat', 'dish', 'gastronomie', 'gastronomy',
                    'table', 'dîner', 'dinner', 'déjeuner', 'lunch', 'horaires', 'hours'
                ],
                'weight': 1.2,
                'icon': 'restaurant',
                'title': 'Restaurant',
                'description': 'Restaurant ou établissement culinaire'
            },
            'health': {
                'keywords': [
                    'santé', 'health', 'médical', 'medical', 'hôpital', 'hospital', 'clinique', 'clinic',
                    'docteur', 'doctor', 'patient', 'traitement', 'treatment', 'consultation',
                    'rendez-vous', 'appointment', 'pharmacie', 'pharmacy', 'soin', 'care'
                ],
                'weight': 1.3,
                'icon': 'local_hospital',
                'title': 'Santé',
                'description': 'Services de santé et médical'
            },
            'real_estate': {
                'keywords': [
                    'immobilier', 'real estate', 'maison', 'house', 'appartement', 'apartment',
                    'vente', 'sale', 'location', 'rent', 'achat', 'buy', 'propriété', 'property',
                    'm²', 'chambre', 'bedroom', 'annonce', 'listing', 'agence', 'agency'
                ],
                'weight': 1.1,
                'icon': 'home',
                'title': 'Immobilier',
                'description': 'Vente et location immobilière'
            },
            'job': {
                'keywords': [
                    'emploi', 'job', 'carrière', 'career', 'recrutement', 'recruitment', 'cv', 'resume',
                    'candidature', 'application', 'offre', 'offer', 'poste', 'position',
                    'salaire', 'salary', 'entreprise', 'company', 'talents', 'hiring'
                ],
                'weight': 1.1,
                'icon': 'work',
                'title': 'Emploi',
                'description': 'Offres d\'emploi et recrutement'
            },
            'travel': {
                'keywords': [
                    'voyage', 'travel', 'tourisme', 'tourism', 'hôtel', 'hotel', 'réservation', 'booking',
                    'vol', 'flight', 'destination', 'vacances', 'vacation', 'séjour', 'stay',
                    'guide', 'visite', 'visit', 'itinéraire', 'itinerary'
                ],
                'weight': 1.0,
                'icon': 'flight',
                'title': 'Voyage & Tourisme',
                'description': 'Services de voyage et tourisme'
            },
            'entertainment': {
                'keywords': [
                    'film', 'movie', 'série', 'series', 'streaming', 'vidéo', 'video',
                    'musique', 'music', 'jeu', 'game', 'divertissement', 'entertainment',
                    'spectacle', 'show', 'concert', 'événement', 'event'
                ],
                'weight': 1.0,
                'icon': 'movie',
                'title': 'Divertissement',
                'description': 'Contenu de divertissement'
            },
            'corporate': {
                'keywords': [
                    'entreprise', 'company', 'corporation', 'business', 'service', 'solution',
                    'about', 'à propos', 'contact', 'équipe', 'team', 'expertise', 'professionnel'
                ],
                'weight': 0.8,
                'icon': 'business',
                'title': 'Site Corporate',
                'description': 'Site d\'entreprise'
            }
        }
        
        # Calculer les scores pour chaque catégorie
        scores = {}
        for category, data in keywords.items():
            score = sum(1 for kw in data['keywords'] if kw in content_to_check)
            scores[category] = score * data['weight']
        
        # Bonus si les champs détectés correspondent
        if detected_fields:
            if 'price' in detected_fields:
                # Réduire le bonus si contexte éducatif
                if scores.get('education', 0) > 3:
                    scores['ecommerce'] = scores.get('ecommerce', 0) + 2  # Bonus réduit
                else:
                    scores['ecommerce'] = scores.get('ecommerce', 0) + 5
            if 'date' in detected_fields:
                scores['blog'] = scores.get('blog', 0) + 3
                scores['news'] = scores.get('news', 0) + 3
            if 'image' in detected_fields and scores.get('portfolio', 0) > 0:
                scores['portfolio'] = scores.get('portfolio', 0) + 4
            # Bonus pour champs éducatifs
            if any(field in detected_fields for field in ['course', 'program', 'student', 'teacher']):
                scores['education'] = scores.get('education', 0) + 5
        
        # Trouver le score maximum
        max_score = max(scores.values()) if scores else 0
        
        if max_score == 0:
            # Aucun mot-clé trouvé
            return {
                'type': 'corporate',
                'title': 'Site Web',
                'icon': 'public',
                'confidence': 0.3,
                'description': 'Site web générique'
            }
        
        # Retourner le type avec le score le plus élevé
        winning_type = max(scores, key=scores.get)
        winning_data = keywords[winning_type]
        
        # Calculer la confiance basée sur le score
        confidence = min(0.95, 0.4 + (scores[winning_type] * 0.05))
        
        return {
            'type': winning_type,
            'title': winning_data['title'],
            'icon': winning_data['icon'],
            'confidence': confidence,
            'description': winning_data['description']
        }
