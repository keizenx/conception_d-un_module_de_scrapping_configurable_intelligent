# Tests du Module de Scraping

Ce dossier contient tous les scripts de test pour valider le fonctionnement du module de scraping.

## 📋 Scripts de test principaux

### 🎯 `test_manual.py` - Test manuel interactif
**Utilisation recommandée pour tester vos propres sites**

```bash
python test_manual.py
```

**Ce qu'il fait :**
- Teste 3 sites par défaut (books.toscrape.com, scrapeme.live, news.ycombinator.com)
- Analyse chaque site pour détecter les collections
- Scrape automatiquement la première collection
- Affiche les résultats de manière claire

**Pour tester vos propres URLs :**
Modifiez la liste `test_sites` dans le script (ligne 103).

---

### 🌐 `test_multi_types.py` - Validation multi-types
**Valide que l'analyse fonctionne sur différents types de pages**

```bash
python test_multi_types.py
```

**Ce qu'il fait :**
- Teste 7 sites de types différents :
  - E-commerce : books.toscrape.com, scrapeme.live
  - Blog/Articles : blog.python.org, realpython.com
  - Actualités : news.ycombinator.com, reddit.com/r/programming
  - Documentation : docs.python.org
- Affiche un résumé de validation par catégorie

---

### 🛒 `test_scraper.py` - Test e-commerce complet
**Test approfondi sur des sites e-commerce**

```bash
python test_scraper.py
```

**Ce qu'il fait :**
- Teste books.toscrape.com et scrapeme.live
- Analyse puis scrape chaque site
- Affiche les détails de chaque item extrait

---

### 🎭 `test_playwright_ready.py` - Vérification Playwright
**Vérifie que Playwright est correctement installé**

```bash
python test_playwright_ready.py
```

**Ce qu'il fait :**
- Teste le mode HTTP classique (use_js=false)
- Teste le mode Playwright (use_js=true)
- Indique si Playwright est opérationnel

---

## 🔍 Scripts de debug

### `debug_analyze.py`
Affiche les candidats détectés par l'algorithme sur books.toscrape.com

```bash
python debug_analyze.py
```

### `debug_scrapeme.py`
Analyse détaillée de la détection sur scrapeme.live

```bash
python debug_scrapeme.py
```

### `debug_signatures.py`
Affiche les signatures des éléments pour comprendre la détection

```bash
python debug_signatures.py
```

### `debug_structure.py`
Analyse la structure HTML d'une page

```bash
python debug_structure.py
```

---

## 🚀 Démarrage rapide

### 1. Démarrer le serveur
```bash
cd ..
..\venv\Scripts\python.exe -m uvicorn src.index:app --reload --port 8000
```

### 2. Lancer les tests
```bash
cd tests
..\venv\Scripts\python.exe test_manual.py
```

---

## 📊 Résultats attendus

Tous les tests doivent afficher :
- ✅ pour les succès
- ❌ pour les échecs
- ⚠️ pour les avertissements

**Taux de réussite attendu : 100%** sur tous les sites de test.

---

## 💡 Conseils

- **Pour sites statiques** : Utilisez `use_js=false` (plus rapide)
- **Pour sites JavaScript** : Utilisez `use_js=true` (nécessite Playwright)
- **Timeout** : Augmentez le timeout pour les sites lents
- **Debug** : Utilisez les scripts `debug_*.py` pour comprendre les détections

---

## 🐛 Dépannage

### Le serveur ne répond pas
Vérifiez que le serveur est démarré sur le port 8000 :
```bash
curl http://localhost:8000/docs
```

### Playwright ne fonctionne pas
Installez les dépendances :
```bash
pip install playwright==1.41.0
playwright install chromium
```

### Aucune collection détectée
- Vérifiez que la page contient des éléments répétitifs
- Utilisez les scripts debug pour analyser la structure
- Essayez avec `use_js=true` si le contenu est chargé en JavaScript
