import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from src.core.perplexity_classifier import PerplexityClassifier

# Tester avec différents sites
classifier = PerplexityClassifier()

test_cases = [
    {
        'url': 'https://iit.ci',
        'title': 'IIT - Institut International de Technologie',
        'text': 'Institut formation campus étudiant programme bachelor master licence cours'
    },
    {
        'url': 'https://amazon.com',
        'title': 'Amazon - Shopping',
        'text': 'buy shop cart price product add to cart checkout delivery'
    },
    {
        'url': 'https://lemonde.fr',
        'title': 'Le Monde - Actualités',
        'text': 'actualité news journal information breaking dernière heure politique'
    },
    {
        'url': 'https://airbnb.com',
        'title': 'Airbnb',
        'text': 'booking hotel voyage travel destination vacances réservation'
    }
]

print("="*60)
print("TEST DU CLASSIFIER")
print("="*60)

for test in test_cases:
    result = classifier._fallback_classification(
        detected_fields=[],
        url=test['url'],
        page_title=test['title'],
        sample_text=test['text']
    )
    
    print(f"\n📍 {test['url']}")
    print(f"   Type: {result['type']}")
    print(f"   Titre: {result['title']}")
    print(f"   Icon: {result['icon']}")
    print(f"   Confiance: {result['confidence']:.0%}")
    print(f"   Description: {result['description']}")
