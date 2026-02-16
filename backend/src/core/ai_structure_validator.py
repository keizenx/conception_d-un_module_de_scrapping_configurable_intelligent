# backend/src/core/ai_structure_validator.py
# Validation intelligente de la structure des sites web
# Utilise l'analyse de patterns pour confirmer les types de contenus détectés
# RELEVANT FILES: content_detector.py, analyzer.py

from typing import Dict, List
from bs4 import BeautifulSoup
import re


class AIStructureValidator:
    """
    Valide si un site web a vraiment la structure détectée.
    Copie et analyse le contenu complet pour confirmer les patterns.
    """
    
    # Patterns sémantiques pour chaque type de contenu
    VALIDATION_PATTERNS = {
        'articles': {
            'html_tags': ['article', 'div[class*="post"]', 'div[class*="article"]'],
            'text_indicators': [
                r'\b(article|blog|post|news|actualit[ée]s?)\b',
                r'\b(auteur|author|par|by|written by)\b',
                r'\b(publi[ée]|published|date|temps de lecture)\b'
            ],
            'structure_markers': ['h1', 'h2', 'h3', 'p', 'time', 'author'],
            'min_text_length': 200,  # Articles doivent avoir du texte substantiel
            'required_elements': 2  # Au moins 2 marqueurs de structure
        },
        'products': {
            'html_tags': ['div[class*="product"]', 'div[itemtype*="Product"]'],
            'text_indicators': [
                r'(€|£|\$|USD|EUR|GBP)\s*\d+',
                r'\b(prix|price|acheter|buy|ajouter au panier|add to cart)\b',
                r'\b(en stock|out of stock|disponible|available)\b',
                r'\b(taille|size|couleur|color|quantit[ée])\b'
            ],
            'structure_markers': ['price', 'add', 'cart', 'stock', 'sku'],
            'min_text_length': 50,
            'required_elements': 2
        },
        'comments': {
            'html_tags': ['div[class*="comment"]', 'div[class*="review"]'],
            'text_indicators': [
                r'\b(commentaire|comment|avis|review|r[ée]ponse|reply)\b',
                r'\b(utile|helpful|signaler|report|like|partager)\b',
                r'\b(il y a|ago|\d+\s*(jour|day|heure|hour|minute|min)s?)\b'
            ],
            'structure_markers': ['author', 'user', 'date', 'time', 'reply'],
            'min_text_length': 20,
            'required_elements': 1
        },
        'reviews': {
            'html_tags': ['div[class*="review"]', 'div[itemtype*="Review"]'],
            'text_indicators': [
                r'(\d+/5|★|⭐|\d+\s*[ée]toile)',
                r'\b(avis v[ée]rifi[ée]|verified|recommande|recommend)\b',
                r'\b(qualit[ée]|quality|service|satisfaction)\b'
            ],
            'structure_markers': ['rating', 'star', 'verified', 'helpful'],
            'min_text_length': 30,
            'required_elements': 1
        },
        'events': {
            'html_tags': ['div[class*="event"]', 'div[itemtype*="Event"]'],
            'text_indicators': [
                r'\b(\d{1,2}\s*(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre))\b',
                r'\b(calendar|calendrier|r[ée]server|register|inscription)\b',
                r'\b(\d{1,2}h\d{2}|\d{1,2}:\d{2})\b'
            ],
            'structure_markers': ['date', 'time', 'location', 'event'],
            'min_text_length': 50,
            'required_elements': 2
        },
        'courses': {
            'html_tags': ['div[class*="course"]', 'div[class*="formation"]'],
            'text_indicators': [
                r'\b(cours|course|formation|training|[ée]tude|study)\b',
                r'\b(niveau|level|d[ée]butant|beginner|avanc[ée]|advanced)\b',
                r'\b(dur[ée]e|duration|heure|hour|module|lesson)\b',
                r'\b(certifi[ée]|certificate|dipl[ôo]me|degree)\b'
            ],
            'structure_markers': ['instructor', 'duration', 'level', 'price'],
            'min_text_length': 100,
            'required_elements': 2
        },
        'jobs': {
            'html_tags': ['div[class*="job"]', 'div[itemtype*="JobPosting"]'],
            'text_indicators': [
                r'\b(emploi|job|poste|position|recrutement|hiring)\b',
                r'\b(salaire|salary|CDI|CDD|temps plein|full.?time)\b',
                r'\b(exp[ée]rience|experience|comp[ée]tence|skill)\b',
                r'\b(postuler|apply|candidature|application)\b'
            ],
            'structure_markers': ['company', 'salary', 'location', 'apply'],
            'min_text_length': 100,
            'required_elements': 2
        },
        'real_estate': {
            'html_tags': ['div[class*="property"]', 'div[class*="listing"]'],
            'text_indicators': [
                r'\b(m²|m2|surface|sqft)\b',
                r'\b(chambre|bedroom|pi[èe]ce|room)\b',
                r'\b(louer|rent|vendre|sale|acheter|buy)\b',
                r'\b(appartement|maison|house|villa|terrain)\b'
            ],
            'structure_markers': ['price', 'surface', 'rooms', 'location'],
            'min_text_length': 80,
            'required_elements': 2
        },
        'recipes': {
            'html_tags': ['div[class*="recipe"]', 'div[itemtype*="Recipe"]'],
            'text_indicators': [
                r'\b(recette|recipe|ingr[ée]dient|ingredient)\b',
                r'\b(cuisson|cooking|pr[ée]paration|preparation)\b',
                r'\b(portion|serving|calorie|minute)\b',
                r'\b([ée]tape|step|instruction|m[ée]lange|mix)\b'
            ],
            'structure_markers': ['ingredients', 'instructions', 'time', 'servings'],
            'min_text_length': 150,
            'required_elements': 2
        }
    }
    
    def validate_content_type(
        self, 
        html_content: str, 
        content_type: str, 
        detected_count: int
    ) -> Dict:
        """
        Valide si le type de contenu détecté est réellement présent.
        
        Args:
            html_content: HTML complet du site
            content_type: Type détecté (articles, products, etc.)
            detected_count: Nombre d'éléments détectés
        
        Returns:
            {
                'valid': bool,
                'confidence': float (0-1),
                'evidence': [liste des preuves trouvées],
                'warnings': [liste des avertissements]
            }
        """
        if content_type not in self.VALIDATION_PATTERNS:
            return {
                'valid': True,  # Si pas de règle, on fait confiance
                'confidence': 0.5,
                'evidence': ['Aucune règle de validation définie'],
                'warnings': []
            }
        
        soup = BeautifulSoup(html_content, 'html.parser')
        pattern = self.VALIDATION_PATTERNS[content_type]
        
        evidence = []
        warnings = []
        score = 0.0
        
        # 1. Vérifier les balises HTML
        html_matches = 0
        for tag_selector in pattern['html_tags']:
            elements = soup.select(tag_selector)
            if elements:
                html_matches += len(elements)
                evidence.append(f"Trouvé {len(elements)} éléments avec {tag_selector}")
        
        if html_matches > 0:
            score += 0.3
        else:
            warnings.append(f"Aucune balise HTML typique de {content_type} trouvée")
        
        # 2. Vérifier les indicateurs textuels
        text_content = soup.get_text().lower()
        text_matches = 0
        
        for regex_pattern in pattern['text_indicators']:
            matches = re.findall(regex_pattern, text_content, re.IGNORECASE)
            if matches:
                text_matches += len(matches)
                evidence.append(f"Pattern textuel '{regex_pattern[:30]}...' trouvé {len(matches)} fois")
        
        if text_matches >= 3:
            score += 0.3
        elif text_matches >= 1:
            score += 0.15
        else:
            warnings.append(f"Peu d'indicateurs textuels pour {content_type}")
        
        # 3. Vérifier les marqueurs de structure
        structure_matches = 0
        for marker in pattern['structure_markers']:
            # Chercher dans les classes, IDs, attributs
            if re.search(rf'\b{marker}\b', html_content, re.IGNORECASE):
                structure_matches += 1
                evidence.append(f"Marqueur de structure '{marker}' présent")
        
        if structure_matches >= pattern['required_elements']:
            score += 0.2
        else:
            warnings.append(f"Seulement {structure_matches}/{pattern['required_elements']} marqueurs requis")
        
        # 4. Vérifier la longueur du texte
        total_text_length = len(text_content)
        
        # Gérer le cas où detected_count est 'N/A' (détection IA sans count)
        count_val = detected_count
        if isinstance(count_val, str) or count_val is None:
            count_val = 1
            
        if total_text_length >= pattern['min_text_length'] * count_val:
            score += 0.2
            evidence.append(f"Longueur de texte suffisante: {total_text_length} caractères")
        else:
            warnings.append(f"Texte court pour {count_val} éléments")
        
        # Décision finale
        is_valid = score >= 0.4  # Seuil de validation
        confidence = min(score, 1.0)
        
        return {
            'valid': is_valid,
            'confidence': round(confidence, 2),
            'evidence': evidence,
            'warnings': warnings,
            'score_details': {
                'html_tags': html_matches,
                'text_indicators': text_matches,
                'structure_markers': structure_matches,
                'text_length': total_text_length
            }
        }
    
    def validate_all_detected_types(
        self, 
        html_content: str, 
        detected_types: List[Dict]
    ) -> Dict:
        """
        Valide tous les types de contenus détectés.
        
        Args:
            html_content: HTML complet
            detected_types: Liste des types détectés par ContentDetector
        
        Returns:
            {
                'validated_types': [types confirmés],
                'rejected_types': [types rejetés],
                'warnings': [avertissements globaux]
            }
        """
        validated = []
        rejected = []
        global_warnings = []
        
        for content_info in detected_types:
            content_type = content_info['type']
            count = content_info['count']
            
            validation = self.validate_content_type(html_content, content_type, count)
            
            if validation['valid']:
                validated.append({
                    **content_info,
                    'validation': validation,
                    'ai_verified': True
                })
            else:
                rejected.append({
                    **content_info,
                    'validation': validation,
                    'ai_verified': False
                })
                global_warnings.append(
                    f"{content_info['name']}: Confiance {validation['confidence']:.0%} - " + 
                    ", ".join(validation['warnings'][:2])
                )
        
        return {
            'validated_types': validated,
            'rejected_types': rejected,
            'warnings': global_warnings,
            'validation_summary': {
                'total_detected': len(detected_types),
                'validated': len(validated),
                'rejected': len(rejected),
                'success_rate': len(validated) / len(detected_types) if detected_types else 0
            }
        }


if __name__ == "__main__":
    # Test
    validator = AIStructureValidator()
    
    test_html = """
    <article class="blog-post">
        <h2>Mon article de blog</h2>
        <p class="author">Par Jean Dupont</p>
        <time>Publié le 15 janvier 2024</time>
        <p>Contenu de l'article avec beaucoup de texte intéressant sur le sujet...</p>
    </article>
    <div class="product">
        <h3>MacBook Pro</h3>
        <span class="price">2499€</span>
        <button>Ajouter au panier</button>
        <span class="stock">En stock</span>
    </div>
    """
    
    print("="*60)
    print("TEST: Validation de Structure par AI")
    print("="*60)
    
    # Test articles
    result = validator.validate_content_type(test_html, 'articles', 1)
    print("\n📰 ARTICLES:")
    print(f"  Valid: {result['valid']}")
    print(f"  Confiance: {result['confidence']:.0%}")
    print(f"  Preuves: {len(result['evidence'])}")
    for ev in result['evidence'][:3]:
        print(f"    - {ev}")
    
    # Test products
    result = validator.validate_content_type(test_html, 'products', 1)
    print("\n🛍️ PRODUITS:")
    print(f"  Valid: {result['valid']}")
    print(f"  Confiance: {result['confidence']:.0%}")
    print(f"  Preuves: {len(result['evidence'])}")
    for ev in result['evidence'][:3]:
        print(f"    - {ev}")
