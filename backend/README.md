# Backend - Module de Scraping Intelligent

Module de scraping configurable et intelligent capable d'analyser et d'extraire automatiquement des données structurées depuis n'importe quel type de page web.

## 🎯 Fonctionnalités

- ✅ **Détection automatique** des collections d'items sur n'importe quelle page web
- ✅ **Extraction intelligente** de tous les champs pertinents (titre, prix, image, lien, description, date, auteur)
- ✅ **Support multi-types** : e-commerce, blog, actualités, documentation, etc.
- ✅ **Mode hybride** : HTTP classique (rapide) ou Playwright (JavaScript)
- ✅ **Filtrage intelligent** : Exclut automatiquement navigation, pagination, menus
- ✅ **Scoring adaptatif** : Priorise les collections avec contenu riche

## 📁 Structure du projet

```
backend/
├── src/
│   ├── api/
│   │   └── routes/
│   │       ├── analyze.py      # Endpoint d'analyse
│   │       ├── scrape.py       # Endpoint de scraping
│   │       └── export.py       # Endpoint d'export
│   ├── core/
│   │   ├── analyzer.py         # Algorithme de détection
│   │   ├── scraper.py          # Extraction des données
│   │   ├── fetcher.py          # HTTP classique
│   │   └── fetcher_playwright.py  # Support JavaScript
│   └── index.py                # Application FastAPI
├── tests/
│   ├── test_manual.py          # Test interactif (recommandé)
│   ├── test_multi_types.py     # Validation multi-types
│   ├── test_scraper.py         # Test e-commerce
│   ├── test_playwright_ready.py # Vérification Playwright
│   └── debug_*.py              # Scripts de debug
├── requirements.txt
├── PROGRESS.md                 # Documentation de progression
└── README.md                   # Ce fichier
```

## 🚀 Installation

### 1. Créer l'environnement virtuel (si pas déjà fait)
```bash
cd ..
python -m venv venv
```

### 2. Activer l'environnement
```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
cd backend
pip install -r requirements.txt
```

### 4. (Optionnel) Installer Playwright pour le support JavaScript
```bash
pip install playwright==1.41.0
playwright install chromium
```

## 🎮 Utilisation

### Démarrer le serveur

```bash
cd backend
..\venv\Scripts\python.exe -m uvicorn src.index:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur : **http://localhost:8000**

### Interface Swagger (recommandé pour débuter)

Ouvrez votre navigateur : **http://localhost:8000/docs**

Vous aurez accès à une interface interactive pour tester les endpoints.

### Tester avec les scripts

```bash
cd tests

# Test manuel interactif (recommandé)
..\venv\Scripts\python.exe test_manual.py

# Validation sur différents types de sites
..\venv\Scripts\python.exe test_multi_types.py

# Test e-commerce spécifique
..\venv\Scripts\python.exe test_scraper.py
```

Voir `tests/README.md` pour plus de détails sur les tests.

## 📡 API Endpoints

### POST /analyze
Analyse une URL et détecte les collections d'items scrapables.

**Paramètres :**
```json
{
  "url": "https://example.com",
  "max_candidates": 5,
  "max_items_preview": 5,
  "use_js": false
}
```

**Réponse :**
```json
{
  "success": true,
  "page_title": "Example Site",
  "summary": {
    "total_collections_found": 2,
    "detected_field_types": ["title", "price", "image", "link"]
  },
  "collections": [...]
}
```

### POST /scrape
Extrait tous les items d'une collection spécifique.

**Paramètres :**
```json
{
  "url": "https://example.com",
  "collection_index": 0,
  "max_items": 1000,
  "use_js": false
}
```

**Réponse :**
```json
{
  "success": true,
  "summary": {
    "total_items_extracted": 20,
    "detected_field_types": ["title", "price", "image", "link"]
  },
  "items": [...]
}
```

## 🎯 Exemples d'utilisation

### Exemple Python avec httpx

```python
import httpx

# 1. Analyser une page
response = httpx.post(
    "http://localhost:8000/analyze",
    json={"url": "https://books.toscrape.com/", "use_js": False}
)
data = response.json()
print(f"Collections trouvées: {data['summary']['total_collections_found']}")

# 2. Scraper la première collection
response = httpx.post(
    "http://localhost:8000/scrape",
    json={"url": "https://books.toscrape.com/", "collection_index": 0}
)
data = response.json()
print(f"Items extraits: {data['summary']['total_items_extracted']}")
```

### Exemple curl

```bash
# Analyser
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/"}'

# Scraper
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://books.toscrape.com/", "collection_index": 0}'
```

## 🧪 Tests et validation

### Taux de réussite actuel : **100% (7/7 sites)**

Sites validés :
- ✅ E-commerce : books.toscrape.com, scrapeme.live
- ✅ Blog : blog.python.org, realpython.com
- ✅ Actualités : news.ycombinator.com, reddit.com
- ✅ Documentation : docs.python.org

Voir `PROGRESS.md` pour les détails complets.

## 🔧 Configuration

### Mode HTTP classique (par défaut)
- Plus rapide
- Fonctionne pour les sites HTML statiques
- `use_js: false`

### Mode Playwright (JavaScript)
- Plus lent mais plus complet
- Nécessaire pour les sites avec contenu dynamique
- Nécessite l'installation de Playwright
- `use_js: true`

## 📊 Performance

- **Analyse** : < 2 secondes (mode HTTP)
- **Scraping** : < 3 secondes pour 50 items (mode HTTP)
- **Mode Playwright** : +5-10 secondes (rendu JavaScript)

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier que le port 8000 est libre
netstat -ano | findstr :8000

# Utiliser un autre port
uvicorn src.index:app --reload --port 8001
```

### Playwright ne fonctionne pas
```bash
# Réinstaller Playwright
pip uninstall playwright
pip install playwright==1.41.0
playwright install chromium
```

### Aucune collection détectée
- Vérifiez que la page contient des éléments répétitifs (au moins 4)
- Essayez avec `use_js: true` si le contenu est chargé en JavaScript
- Utilisez les scripts de debug dans `tests/` pour analyser la structure

## 📚 Documentation

- `PROGRESS.md` : Progression détaillée et améliorations
- `tests/README.md` : Guide des tests
- Swagger UI : http://localhost:8000/docs

## 🔮 Prochaines étapes

- [ ] Support de la pagination automatique
- [ ] Détection et suivi des liens "Next"
- [ ] Export en différents formats (CSV, JSON, Excel)
- [ ] Cache et optimisation des requêtes

## 📝 Licence

MIT
