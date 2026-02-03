# backend/tests/demo_content_detection.py
# Démonstration du système de détection de contenus
# Montre tous les types de contenus détectables
# RELEVANT FILES: content_detector.py

import sys
sys.path.insert(0, '..')

from src.core.content_detector import ContentDetector

# HTML simulé avec différents types de contenus
DEMO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Site E-commerce & Blog - Exemple</title>
</head>
<body>
    <!-- Navigation -->
    <nav class="main-menu">
        <a href="/">Accueil</a>
        <a href="/shop">Boutique</a>
        <a href="/blog">Blog</a>
    </nav>
    
    <!-- Articles de blog -->
    <article class="post">
        <h2 class="title">Les 10 meilleurs laptops 2024</h2>
        <p class="author">Par Jean Martin</p>
        <span class="date">15 janvier 2024</span>
        <div class="content">
            <p>Découvrez notre sélection des meilleurs ordinateurs portables...</p>
        </div>
        <img src="/img1.jpg" alt="Laptop">
    </article>
    
    <article class="post">
        <h2 class="title">Guide d'achat: comment choisir son PC</h2>
        <p class="author">Par Marie Dubois</p>
        <div class="content">Article complet sur le choix d'un PC...</div>
    </article>
    
    <article class="blog-post">
        <h3>Nouveautés tech de la semaine</h3>
        <p>Toutes les nouveautés...</p>
    </article>
    
    <!-- Produits e-commerce -->
    <div class="product">
        <h3 class="name">MacBook Pro 16"</h3>
        <span class="price">2499.99€</span>
        <p class="description">Processeur M2 Pro, 16GB RAM, 512GB SSD</p>
        <img src="/macbook.jpg">
        <div class="rating">4.8/5</div>
        <span class="stock">En stock</span>
    </div>
    
    <div class="product-card">
        <h3 class="name">Dell XPS 15</h3>
        <span class="price">1899€</span>
        <p>Intel i7, 16GB, RTX 3050</p>
    </div>
    
    <div class="product-item" itemtype="http://schema.org/Product">
        <span itemprop="name">Lenovo ThinkPad</span>
        <span itemprop="price">1299€</span>
    </div>
    
    <!-- Avis/Reviews -->
    <div class="review">
        <div class="author">Pierre L.</div>
        <div class="rating">5 étoiles</div>
        <p class="text">Excellent produit, très satisfait de mon achat!</p>
        <span class="date">Il y a 2 jours</span>
        <span class="verified">Achat vérifié</span>
    </div>
    
    <div class="review">
        <div class="author">Sophie M.</div>
        <div class="rating">4/5</div>
        <p>Bon rapport qualité-prix</p>
    </div>
    
    <!-- Commentaires -->
    <div class="comment">
        <span class="author">Thomas</span>
        <p>Super article, très utile!</p>
        <span class="date">Aujourd'hui</span>
    </div>
    
    <div class="comment">
        <span class="author">Julie</span>
        <p>Merci pour ces conseils</p>
    </div>
    
    <!-- Événements -->
    <div class="event">
        <h3>Conférence Tech 2024</h3>
        <span class="date">25 mars 2024</span>
        <span class="location">Paris</span>
        <p class="description">Grande conférence annuelle sur la tech</p>
        <span class="price">Gratuit</span>
    </div>
    
    <!-- Cours -->
    <div class="course">
        <h3>Formation Python Avancé</h3>
        <p class="description">Apprenez Python de A à Z</p>
        <span class="duration">40 heures</span>
        <span class="instructor">Dr. Dupont</span>
        <span class="level">Intermédiaire</span>
    </div>
    
    <!-- FAQ -->
    <div class="faq">
        <div class="question">Comment passer commande?</div>
        <div class="answer">Il suffit de cliquer sur "Acheter"...</div>
    </div>
    
    <!-- Formulaire -->
    <form class="contact-form">
        <input type="text" placeholder="Nom">
        <input type="email" placeholder="Email">
        <textarea placeholder="Message"></textarea>
        <button>Envoyer</button>
    </form>
    
    <!-- Images -->
    <div class="gallery">
        <img src="/img1.jpg" alt="Photo 1">
        <img src="/img2.jpg" alt="Photo 2">
        <img src="/img3.jpg" alt="Photo 3">
    </div>
    
    <!-- Tableaux -->
    <table class="data-table">
        <thead>
            <tr>
                <th>Modèle</th>
                <th>Prix</th>
                <th>Stock</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>MacBook Pro</td>
                <td>2499€</td>
                <td>5</td>
            </tr>
            <tr>
                <td>Dell XPS</td>
                <td>1899€</td>
                <td>12</td>
            </tr>
        </tbody>
    </table>
    
    <!-- Pagination -->
    <div class="pagination">
        <a href="?page=1">1</a>
        <a href="?page=2" class="active">2</a>
        <a href="?page=3">3</a>
        <a href="?page=4">4</a>
        <a href="?page=5">5</a>
        <a class="next" href="?page=3">Suivant</a>
    </div>
    
    <!-- Contacts -->
    <div class="contact">
        <p class="phone">+33 1 23 45 67 89</p>
        <p class="email">contact@example.com</p>
        <p class="address">123 Rue de Paris, 75001 Paris</p>
        <p class="hours">Lun-Ven: 9h-18h</p>
    </div>
    
    <!-- Réseaux sociaux -->
    <div class="social-links">
        <a href="https://facebook.com">Facebook</a>
        <a href="https://twitter.com">Twitter</a>
        <a href="https://instagram.com">Instagram</a>
    </div>
</body>
</html>
"""

def main():
    print("\n" + "="*70)
    print("DÉMONSTRATION: Détection Intelligente de Contenus Scrapables")
    print("="*70)
    
    detector = ContentDetector()
    result = detector.detect_content_types(DEMO_HTML, "https://example.com")
    
    print(f"\n📊 STATISTIQUES GLOBALES")
    print("-" * 70)
    print(f"Total de types détectés: {result['total_types']}")
    print(f"Action recommandée: {result['recommended_action']}")
    print(f"Complexité de la structure: {result['structure_complexity']}")
    print(f"Pagination détectée: {'Oui' if result['has_pagination'] else 'Non'}")
    print(f"Nombre de pages estimé: {result['total_pages_estimate']}")
    
    print(f"\n{'='*70}")
    print(f"📦 TYPES DE CONTENUS DISPONIBLES POUR LE SCRAPING")
    print(f"{'='*70}")
    
    for i, content in enumerate(result['detected_types'], 1):
        print(f"\n{i}. {content['icon']} {content['name']}")
        print(f"   └─ Type: {content['type']}")
        print(f"   └─ Éléments trouvés: {content['count']}")
        print(f"   └─ Niveau de confiance: {content['confidence']:.0%}")
        print(f"   └─ Description: {content['description']}")
        print(f"   └─ Champs disponibles: {', '.join(content['fields']) if content['fields'] else 'N/A'}")
        
        if content.get('sample'):
            print(f"   └─ Aperçu:")
            for key, value in list(content['sample'].items())[:3]:
                preview = str(value)[:70] + '...' if len(str(value)) > 70 else str(value)
                print(f"      • {key}: {preview}")
    
    print(f"\n{'='*70}")
    print(f"✨ OPTIONS DE SCRAPING")
    print(f"{'='*70}")
    print("\nL'utilisateur peut maintenant:")
    print("\n  1️⃣  Scraper TOUT le site")
    print(f"     → {result['total_types']} types de contenus, tous les éléments")
    
    print("\n  2️⃣  Scraper des types SPÉCIFIQUES")
    print("     Par exemple:")
    for content in result['detected_types'][:5]:
        print(f"     → Uniquement {content['name']} ({content['count']} éléments)")
    
    print("\n  3️⃣  Combinaison PERSONNALISÉE")
    print("     Par exemple:")
    print("     → Articles + Produits + Reviews")
    print("     → Navigation + Images + Formulaires")
    print("     → Tout sauf Pagination")
    
    print(f"\n{'='*70}")
    print("✅ Le système détecte automatiquement la structure du site")
    print("   et permet un scraping précis et efficace!")
    print("="*70)

if __name__ == "__main__":
    main()
