# backend/src/core/content_detector.py
# Détection intelligente des types de contenus scrapables sur un site web
# Identifie articles, commentaires, produits, images, etc.
# RELEVANT FILES: analyzer.py, metadata_classifier.py

from typing import Dict, List
from bs4 import BeautifulSoup
import re


class ContentDetector:
    """
    Détecte tous les types de contenus scrapables sur une page web.
    Permet de choisir précisément quoi scraper ou tout scraper d'un coup.
    """
    
    # Définition de tous les types de contenus détectables
    CONTENT_TYPES = {
        'vehicles': {
            'name': 'Véhicules & Auto',
            'icon': 'directions_car',
            'selectors': ['.vehicle', '.car', '[itemtype*="Vehicle"]', '[itemtype*="Car"]', '.model', '.trim', '.inventory-item'],
            'required_elements': ['model'],
            'optional_elements': ['price', 'range', 'acceleration', 'speed', 'specs', 'features'],
            'description': 'Voitures, spécifications, modèles'
        },
        'tech_specs': {
            'name': 'Spécifications Techniques',
            'icon': 'memory',
            'selectors': ['.specs', '.specifications', '.features', '.tech-specs', '.parameters'],
            'required_elements': ['specs'],
            'optional_elements': ['dimensions', 'weight', 'performance', 'battery', 'display'],
            'description': 'Caractéristiques techniques détaillées'
        },
        'articles': {
            'name': 'Articles de Blog/News',
            'icon': 'article',
            'selectors': ['article', '.post', '.article', '.blog-post', '.news-item', '[itemtype*="Article"]'],
            'required_elements': ['title', 'content'],
            'optional_elements': ['author', 'date', 'category', 'tags', 'image'],
            'description': 'Articles, posts de blog, actualités'
        },
        'products': {
            'name': 'Produits E-commerce',
            'icon': 'shopping_bag',
            'selectors': ['.product', '.item', '[itemtype*="Product"]', '.product-card', '.product-item', '.card', '.listing-item'],
            'required_elements': ['price'], # Nom souvent implicite ou dans un lien, prix est le marqueur fort
            'optional_elements': ['description', 'image', 'sku', 'rating', 'reviews', 'stock', 'name'],
            'description': 'Produits avec prix, descriptions, images'
        },
        'comments': {
            'name': 'Commentaires',
            'icon': 'comment',
            'selectors': ['.comment', '.review', '[class*="comment"]', '#comments', '.discussion'],
            'required_elements': ['author', 'text'],
            'optional_elements': ['date', 'rating', 'likes', 'replies'],
            'description': 'Commentaires, avis, discussions'
        },
        'reviews': {
            'name': 'Avis/Reviews',
            'icon': 'star',
            'selectors': ['.review', '[itemtype*="Review"]', '.rating', '.testimonial'],
            'required_elements': ['rating', 'text'],
            'optional_elements': ['author', 'date', 'verified', 'helpful'],
            'description': 'Avis clients, notes, témoignages'
        },
        'events': {
            'name': 'Événements',
            'icon': 'event',
            'selectors': ['.event', '[itemtype*="Event"]', '.calendar-item', '.schedule'],
            'required_elements': ['name', 'date'],
            'optional_elements': ['location', 'description', 'time', 'price'],
            'description': 'Événements, dates, calendriers'
        },
        'jobs': {
            'name': 'Offres d\'Emploi',
            'icon': 'work',
            'selectors': ['.job', '.job-listing', '[itemtype*="JobPosting"]', '.career'],
            'required_elements': ['title', 'company'],
            'optional_elements': ['location', 'salary', 'description', 'requirements'],
            'description': 'Offres d\'emploi, postes, carrières'
        },
        'courses': {
            'name': 'Cours/Formations',
            'icon': 'school',
            'selectors': ['.course', '.program', '[itemtype*="Course"]', '.formation', '.training'],
            'required_elements': ['name'],
            'optional_elements': ['description', 'duration', 'instructor', 'price', 'level'],
            'description': 'Cours, formations, programmes éducatifs'
        },
        'recipes': {
            'name': 'Recettes',
            'icon': 'restaurant',
            'selectors': ['.recipe', '[itemtype*="Recipe"]', '.recette'],
            'required_elements': ['name', 'ingredients'],
            'optional_elements': ['instructions', 'time', 'servings', 'image', 'rating'],
            'description': 'Recettes de cuisine'
        },
        'real_estate': {
            'name': 'Biens Immobiliers',
            'icon': 'home',
            'selectors': ['.property', '.listing', '[itemtype*="RealEstateListing"]', '.annonce'],
            'required_elements': ['title', 'price'],
            'optional_elements': ['location', 'surface', 'rooms', 'description', 'images'],
            'description': 'Maisons, appartements, terrains'
        },
        'media': {
            'name': 'Images & Médias',
            'icon': 'photo_library',
            'selectors': ['.gallery', '.image', 'img', 'video', '.media'],
            'required_elements': ['src'],
            'optional_elements': ['alt', 'caption', 'title', 'dimensions'],
            'description': 'Images, vidéos, médias'
        },
        'tables': {
            'name': 'Tableaux de Données',
            'icon': 'table_chart',
            'selectors': ['table', '.data-table', '.grid'],
            'required_elements': ['headers', 'rows'],
            'optional_elements': [],
            'description': 'Tableaux structurés avec données'
        },
        'forms': {
            'name': 'Formulaires',
            'icon': 'description',
            'selectors': ['form', '.form', '.contact-form'],
            'required_elements': ['fields'],
            'optional_elements': ['labels', 'placeholders', 'validation'],
            'description': 'Formulaires de contact, inscription'
        },
        'profiles': {
            'name': 'Profils Utilisateurs',
            'icon': 'person',
            'selectors': ['.profile', '.user', '[itemtype*="Person"]', '.member'],
            'required_elements': ['name'],
            'optional_elements': ['bio', 'image', 'social', 'skills', 'experience'],
            'description': 'Profils, membres, équipes'
        },
        'faq': {
            'name': 'FAQ/Questions',
            'icon': 'help',
            'selectors': ['.faq', '.question', '[itemtype*="Question"]', '.qa'],
            'required_elements': ['question', 'answer'],
            'optional_elements': ['category'],
            'description': 'Questions fréquentes, Q&A'
        },
        'navigation': {
            'name': 'Navigation/Menus',
            'icon': 'menu',
            'selectors': ['nav', '.menu', '.navigation', 'header'],
            'required_elements': ['links'],
            'optional_elements': ['categories', 'hierarchy'],
            'description': 'Menus, liens de navigation'
        },
        'contacts': {
            'name': 'Contacts/Coordonnées',
            'icon': 'contact_phone',
            'selectors': ['.contact', '[itemtype*="ContactPoint"]', '.address'],
            'required_elements': ['info'],
            'optional_elements': ['phone', 'email', 'address', 'hours'],
            'description': 'Coordonnées, adresses, horaires'
        },
        'social': {
            'name': 'Liens Sociaux',
            'icon': 'share',
            'selectors': ['.social', '.social-links', '.social-media'],
            'required_elements': ['links'],
            'optional_elements': ['platform', 'handle'],
            'description': 'Liens réseaux sociaux'
        },
        'pagination': {
            'name': 'Pagination',
            'icon': 'view_list',
            'selectors': ['.pagination', '.pager', '.page-numbers'],
            'required_elements': ['pages'],
            'optional_elements': ['total', 'current'],
            'description': 'Navigation entre pages'
        },
        'text_content': {
            'name': 'Contenu Textuel',
            'icon': 'subject',
            'selectors': ['p', '.content', '.text', 'main'],
            'required_elements': ['text'],
            'optional_elements': ['headings', 'lists'],
            'description': 'Paragraphes, textes principaux'
        }
    }
    
    def detect_content_types(self, html_content: str, url: str = '') -> Dict:
        """
        Analyse une page HTML et détecte tous les types de contenus présents.
        
        Args:
            html_content: Contenu HTML de la page
            url: URL de la page (optionnel)
        
        Returns:
            {
                'detected_types': [
                    {
                        'type': 'articles',
                        'name': 'Articles de Blog/News',
                        'icon': 'article',
                        'count': 15,
                        'sample': {...},
                        'confidence': 0.9,
                        'scrapable': True,
                        'fields': ['title', 'author', 'date', 'content']
                    },
                    ...
                ],
                'total_types': 5,
                'recommended_action': 'selective' | 'full_site',
                'structure_complexity': 'simple' | 'medium' | 'complex'
            }
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        detected = []
        
        for content_type, config in self.CONTENT_TYPES.items():
            # Chercher les éléments de ce type
            elements = []
            for selector in config['selectors']:
                try:
                    found = soup.select(selector)
                    elements.extend(found)
                except:
                    continue
            
            if not elements:
                continue
            
            # Limiter à 50 éléments max pour l'analyse
            elements = elements[:50]
            
            # Analyser les éléments trouvés
            count = len(elements)
            sample_data = self._extract_sample(elements[0], content_type) if elements else None
            fields_found = self._identify_fields(elements, config)
            
            # Calculer la confiance
            confidence = self._calculate_confidence(elements, config, fields_found)
            
            if confidence > 0.3:  # Seuil minimum de confiance
                detected.append({
                    'type': content_type,
                    'name': config['name'],
                    'icon': config['icon'],
                    'description': config['description'],
                    'count': count,
                    'sample': sample_data,
                    'confidence': round(confidence, 2),
                    'scrapable': True,
                    'fields': fields_found,
                    'required_fields': config['required_elements'],
                    'optional_fields': config['optional_elements']
                })
        
        # Trier par confiance décroissante
        detected.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Recommandation
        recommendation = 'selective' if len(detected) <= 3 else 'full_site'
        
        # Complexité de la structure
        complexity = 'simple' if len(detected) <= 2 else 'medium' if len(detected) <= 5 else 'complex'
        
        return {
            'detected_types': detected,
            'total_types': len(detected),
            'recommended_action': recommendation,
            'structure_complexity': complexity,
            'has_pagination': self._detect_pagination(soup),
            'total_pages_estimate': self._estimate_total_pages(soup)
        }
    
    def _extract_sample(self, element, content_type: str) -> Dict:
        """Extrait un échantillon de données d'un élément."""
        sample = {}
        
        # Extraction basée sur le type
        if content_type == 'vehicles':
            sample['model'] = self._get_text(element, ['.model', '.name', 'h1', 'h2'])
            sample['specs'] = self._get_text(element, ['.specs', '.features', '.range', '.acceleration'])
        elif content_type == 'tech_specs':
            sample['specs'] = self._get_text(element, ['.value', '.data', 'td', 'li'])
        elif content_type == 'articles':
            sample['title'] = self._get_text(element, ['h1', 'h2', 'h3', '.title', '.headline'])
            sample['text'] = element.get_text(strip=True)[:200] + '...'
        elif content_type == 'products':
            sample['name'] = self._get_text(element, ['.name', '.title', 'h2', 'h3'])
            sample['price'] = self._get_text(element, ['.price', '.cost', '[itemprop="price"]'])
        elif content_type == 'comments':
            sample['author'] = self._get_text(element, ['.author', '.user', '.name'])
            sample['text'] = element.get_text(strip=True)[:150] + '...'
        else:
            sample['text'] = element.get_text(strip=True)[:200] + '...'
        
        return sample
    
    def _get_text(self, element, selectors: List[str]) -> str:
        """Cherche du texte dans un élément avec plusieurs sélecteurs."""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found:
                    return found.get_text(strip=True)
            except:
                continue
        return element.get_text(strip=True)[:100]
    
    def _identify_fields(self, elements, config: Dict) -> List[str]:
        """Identifie quels champs sont présents dans les éléments."""
        fields = []
        
        # Vérifier chaque élément requis et optionnel
        all_fields = config['required_elements'] + config['optional_elements']
        
        for field in all_fields:
            # Chercher des indices de ce champ dans les éléments
            found = False
            for elem in elements[:5]:  # Vérifier les 5 premiers
                # Conversion en string pour chercher dans les attributs (class, id, etc)
                elem_str = str(elem).lower()
                elem_text = elem.get_text().lower()
                
                # Recherche plus large : dans le texte, les classes, les attributs
                if (field in elem_text) or \
                   (f'{field}' in elem_str) or \
                   (field == 'price' and any(curr in elem_text for curr in ['€', '$', '£', 'fcfa', 'xof'])) or \
                   (field == 'image' and elem.find('img')) or \
                   (field == 'model' and any(kw in elem_text for kw in ['model', 'modèle', 'série', 'edition'])) or \
                   (field == 'specs' and any(kw in elem_text for kw in ['km/h', 'mph', '0-60', 'autonomie', 'range', 'battery', 'wh'])):
                    found = True
                    break
            
            if found:
                fields.append(field)
        
        return fields
    
    def _calculate_confidence(self, elements, config: Dict, fields_found: List[str]) -> float:
        """Calcule le score de confiance pour un type de contenu."""
        if not elements:
            return 0.0
        
        # Facteurs de confiance
        count_score = min(len(elements) / 10, 0.4)  # Max 0.4 pour la quantité
        
        # Champs requis présents
        required_present = sum(1 for f in config['required_elements'] if f in fields_found)
        required_score = (required_present / len(config['required_elements'])) * 0.4 if config['required_elements'] else 0.2
        
        # Champs optionnels présents (bonus)
        optional_present = sum(1 for f in config['optional_elements'] if f in fields_found)
        optional_score = (optional_present / max(len(config['optional_elements']), 1)) * 0.2
        
        return min(count_score + required_score + optional_score, 1.0)
    
    def _detect_pagination(self, soup: BeautifulSoup) -> bool:
        """Détecte si la page a une pagination."""
        pagination_selectors = ['.pagination', '.pager', '.page-numbers', '.next', '.previous', 'a[rel="next"]']
        for selector in pagination_selectors:
            if soup.select(selector):
                return True
        return False
    
    def _estimate_total_pages(self, soup: BeautifulSoup) -> int:
        """Estime le nombre total de pages basé sur la pagination."""
        # Chercher des indicateurs de nombre de pages
        pagination = soup.select('.pagination, .pager')
        if pagination:
            # Chercher des numéros de page
            numbers = []
            for elem in pagination:
                text = elem.get_text()
                found_numbers = re.findall(r'\d+', text)
                numbers.extend([int(n) for n in found_numbers])
            
            if numbers:
                return max(numbers)
        
        return 1


if __name__ == "__main__":
    # Test
    detector = ContentDetector()
    
    test_html = """
    <html>
        <body>
            <article class="post">
                <h2 class="title">Mon Article</h2>
                <p class="author">Jean Dupont</p>
                <div class="content">Contenu de l'article...</div>
            </article>
            <div class="product">
                <h3 class="name">Produit 1</h3>
                <span class="price">99.99€</span>
            </div>
            <div class="comment">
                <span class="author">Utilisateur</span>
                <p>Super article!</p>
            </div>
        </body>
    </html>
    """
    
    result = detector.detect_content_types(test_html)
    
    print("="*60)
    print("TYPES DE CONTENU DÉTECTÉS")
    print("="*60)
    print(f"\nTotal: {result['total_types']} types")
    print(f"Recommandation: {result['recommended_action']}")
    print(f"Complexité: {result['structure_complexity']}\n")
    
    for content in result['detected_types']:
        print(f"\n{content['icon']} {content['name']}")
        print(f"   Quantité: {content['count']} éléments")
        print(f"   Confiance: {content['confidence']:.0%}")
        print(f"   Champs: {', '.join(content['fields'])}")
