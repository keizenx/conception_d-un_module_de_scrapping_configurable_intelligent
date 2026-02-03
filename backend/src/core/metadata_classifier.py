# backend/src/core/metadata_classifier.py
# Classification de sites web via métadonnées OpenGraph et Schema.org
# 100% gratuit - utilise les métadonnées déjà présentes sur les sites
# RELEVANT FILES: perplexity_classifier.py, analyzer.py

from typing import Dict, Optional
from bs4 import BeautifulSoup
import httpx
import json


class MetadataClassifier:
    """
    Classifie les sites web en analysant leurs métadonnées (OpenGraph, Schema.org, etc.)
    Alternative gratuite à Perplexity pour la classification de base.
    """
    
    # Mapping des types Schema.org vers nos catégories
    SCHEMA_MAPPING = {
        'EducationalOrganization': 'education',
        'CollegeOrUniversity': 'education',
        'School': 'education',
        'OnlineCourse': 'education',
        'Course': 'education',
        'Store': 'ecommerce',
        'OnlineStore': 'ecommerce',
        'Product': 'ecommerce',
        'Offer': 'ecommerce',
        'NewsArticle': 'news',
        'NewsMediaOrganization': 'news',
        'Blog': 'blog',
        'BlogPosting': 'blog',
        'Restaurant': 'restaurant',
        'FoodEstablishment': 'restaurant',
        'Hotel': 'travel',
        'TravelAgency': 'travel',
        'TouristAttraction': 'travel',
        'Hospital': 'health',
        'MedicalOrganization': 'health',
        'Physician': 'health',
        'JobPosting': 'job',
        'RealEstateAgent': 'real_estate',
        'Residence': 'real_estate',
        'GovernmentOrganization': 'government',
        'NGO': 'nonprofit',
        'MovieTheater': 'entertainment',
        'MusicGroup': 'entertainment',
        'SportsOrganization': 'sports',
        'SportsTeam': 'sports',
        'Organization': 'corporate',
        'Corporation': 'corporate',
        'LocalBusiness': 'corporate'
    }
    
    # Mapping des types OG (OpenGraph) vers nos catégories
    OG_TYPE_MAPPING = {
        'website': None,  # Trop générique
        'article': 'blog',
        'blog': 'blog',
        'product': 'ecommerce',
        'product.group': 'ecommerce',
        'product.item': 'ecommerce',
        'video.movie': 'entertainment',
        'video.episode': 'entertainment',
        'music.song': 'entertainment',
        'music.album': 'entertainment',
        'book': 'documentation',
        'profile': 'social',
        'restaurant.restaurant': 'restaurant',
        'restaurant.menu': 'restaurant'
    }
    
    # Icons pour chaque type
    ICONS = {
        'education': 'school',
        'ecommerce': 'shopping_cart',
        'news': 'newspaper',
        'blog': 'article',
        'restaurant': 'restaurant',
        'travel': 'flight',
        'health': 'local_hospital',
        'job': 'work',
        'real_estate': 'home',
        'government': 'account_balance',
        'nonprofit': 'volunteer_activism',
        'entertainment': 'movie',
        'sports': 'sports_soccer',
        'corporate': 'business',
        'social': 'people',
        'documentation': 'description'
    }
    
    # Titres pour chaque type
    TITLES = {
        'education': 'Établissement Éducatif',
        'ecommerce': 'E-commerce',
        'news': 'Site d\'Actualités',
        'blog': 'Blog',
        'restaurant': 'Restaurant',
        'travel': 'Voyage & Tourisme',
        'health': 'Santé',
        'job': 'Emploi',
        'real_estate': 'Immobilier',
        'government': 'Site Gouvernemental',
        'nonprofit': 'Organisation à But Non Lucratif',
        'entertainment': 'Divertissement',
        'sports': 'Sports',
        'corporate': 'Site Corporate',
        'social': 'Réseau Social',
        'documentation': 'Documentation'
    }
    
    # Descriptions pour chaque type
    DESCRIPTIONS = {
        'education': 'École, université ou centre de formation',
        'ecommerce': 'Site de vente en ligne',
        'news': 'Média d\'information et actualités',
        'blog': 'Blog personnel ou professionnel',
        'restaurant': 'Restaurant ou établissement culinaire',
        'travel': 'Services de voyage et tourisme',
        'health': 'Services de santé et médical',
        'job': 'Offres d\'emploi et recrutement',
        'real_estate': 'Vente et location immobilière',
        'government': 'Site officiel du gouvernement',
        'nonprofit': 'Organisation caritative ou associative',
        'entertainment': 'Contenu de divertissement',
        'sports': 'Sports et activités sportives',
        'corporate': 'Site d\'entreprise',
        'social': 'Plateforme de réseau social',
        'documentation': 'Documentation technique ou guide'
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def classify_from_metadata(self, html_content: str, url: str = '') -> Optional[Dict]:
        """
        Analyse les métadonnées d'une page HTML pour déterminer sa catégorie.
        
        Args:
            html_content: Le contenu HTML de la page
            url: L'URL de la page (optionnel)
        
        Returns:
            Dict avec type, title, icon, confidence, description ou None
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Chercher les balises Schema.org (JSON-LD)
        schema_type = self._extract_schema_type(soup)
        if schema_type and schema_type in self.SCHEMA_MAPPING:
            category = self.SCHEMA_MAPPING[schema_type]
            return {
                'type': category,
                'title': self.TITLES.get(category, 'Site Web'),
                'icon': self.ICONS.get(category, 'public'),
                'confidence': 0.90,
                'description': self.DESCRIPTIONS.get(category, 'Site web'),
                'source': 'schema.org'
            }
        
        # 2. Chercher les balises OpenGraph
        og_type = self._extract_og_type(soup)
        if og_type and og_type in self.OG_TYPE_MAPPING:
            category = self.OG_TYPE_MAPPING[og_type]
            if category:
                return {
                    'type': category,
                    'title': self.TITLES.get(category, 'Site Web'),
                    'icon': self.ICONS.get(category, 'public'),
                    'confidence': 0.80,
                    'description': self.DESCRIPTIONS.get(category, 'Site web'),
                    'source': 'opengraph'
                }
        
        # 3. Analyser les meta keywords/description
        meta_category = self._extract_from_meta(soup)
        if meta_category:
            return {
                'type': meta_category,
                'title': self.TITLES.get(meta_category, 'Site Web'),
                'icon': self.ICONS.get(meta_category, 'public'),
                'confidence': 0.70,
                'description': self.DESCRIPTIONS.get(meta_category, 'Site web'),
                'source': 'meta'
            }
        
        return None
    
    def _extract_schema_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le type depuis Schema.org (JSON-LD)."""
        # Chercher les scripts JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Peut être un objet ou une liste d'objets
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Extraire @type
                schema_type = data.get('@type')
                if schema_type:
                    # Peut être une liste de types
                    if isinstance(schema_type, list):
                        schema_type = schema_type[0]
                    return schema_type
            except:
                continue
        
        return None
    
    def _extract_og_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le type depuis OpenGraph."""
        og_type = soup.find('meta', property='og:type')
        if og_type and og_type.get('content'):
            return og_type['content']
        return None
    
    def _extract_from_meta(self, soup: BeautifulSoup) -> Optional[str]:
        """Tente de classifier à partir des meta keywords/description."""
        # Meta description
        description = soup.find('meta', attrs={'name': 'description'})
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        
        text = ''
        if description and description.get('content'):
            text += description['content'].lower() + ' '
        if keywords and keywords.get('content'):
            text += keywords['content'].lower() + ' '
        
        if not text:
            return None
        
        # Recherche par mots-clés
        if any(kw in text for kw in ['école', 'university', 'formation', 'student']):
            return 'education'
        elif any(kw in text for kw in ['shop', 'buy', 'cart', 'store']):
            return 'ecommerce'
        elif any(kw in text for kw in ['news', 'actualité', 'journal']):
            return 'news'
        elif any(kw in text for kw in ['blog', 'article', 'post']):
            return 'blog'
        elif any(kw in text for kw in ['restaurant', 'menu', 'cuisine']):
            return 'restaurant'
        
        return None
    
    def fetch_and_classify(self, url: str) -> Optional[Dict]:
        """
        Récupère une URL et classifie le site.
        
        Args:
            url: URL à analyser
        
        Returns:
            Dict avec classification ou None
        """
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers={'User-Agent': self.user_agent})
                
                if response.status_code == 200:
                    return self.classify_from_metadata(response.text, url)
        except Exception as e:
            print(f"[!] Erreur fetch metadata: {e}")
        
        return None


if __name__ == "__main__":
    # Test
    classifier = MetadataClassifier()
    
    test_urls = [
        'https://www.sorbonne-universite.fr/',
        'https://www.amazon.fr/',
        'https://www.lemonde.fr/',
    ]
    
    print("="*60)
    print("TEST METADATA CLASSIFIER")
    print("="*60)
    
    for url in test_urls:
        print(f"\n🔍 {url}")
        result = classifier.fetch_and_classify(url)
        if result:
            print(f"   ✅ Type: {result['type']}")
            print(f"   Titre: {result['title']}")
            print(f"   Confiance: {result['confidence']:.0%}")
            print(f"   Source: {result['source']}")
        else:
            print("   ❌ Pas de métadonnées")
