# 🚀 Scraper Pro - Module de Scraping Configurable & Intelligent

> Plateforme complète de web scraping avec intelligence artificielle, analyse automatique et notifications en temps réel.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table des Matières

- [Aperçu](#-aperçu)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Technologies](#-technologies)
- [API Documentation](#-api-documentation)
- [Contribution](#-contribution)

## 🎯 Aperçu

**Scraper Pro** est une solution complète de web scraping intelligent qui permet d'extraire, analyser et exporter des données web de manière automatisée et configurable. Avec son interface moderne et intuitive, il offre une expérience utilisateur optimale pour les professionnels du data scraping.

### ✨ Points Forts

- 🤖 **Analyse Intelligente** - Détection automatique du contenu scrapable
- ⚡ **Mode Asynchrone** - Navigation libre pendant le scraping
- 🔔 **Notifications Temps Réel** - Son + notifications browser
- 📊 **Multi-Format Export** - CSV, Excel, JSON, XML, PDF, ZIP Images
- 🎨 **Interface Moderne** - Design dark mode élégant
- 🔐 **Authentification Complète** - Système de login/register sécurisé
- 📈 **Dashboard Analytique** - Visualisation des sessions et statistiques
- 🎯 **Sélection Personnalisée** - Choix précis des éléments à exporter

## 👥 L'Équipe

*   **Front-end :** Koffi Ornella (Dev), Kouame Aka Richard (PO)
*   **Back-end :** Oumar Vivien (Dev), Kouakou Jean Raphael (Dev)
*   **Gestion :** Beleley Franck (Scrum Master)

## 🌟 Fonctionnalités Principales

### 1. Analyse Automatique du Site
- ✅ Détection automatique des types de contenu (titres, paragraphes, images, liens, etc.)
- ✅ Estimation du nombre de pages
- ✅ Vérification de l'accessibilité et protection anti-scraping
- ✅ Détection de la stack technologique
- ✅ Découverte des sous-domaines scrapables

### 2. Scraping Configurable
- ✅ Sélection des types de contenu à extraire
- ✅ Profondeur de crawling configurable
- ✅ Délai entre les requêtes personnalisable
- ✅ User-Agent customisable
- ✅ Sélecteurs CSS personnalisés
- ✅ Mode avec/sans sous-domaines

### 3. Export Multi-Format
- 📄 **CSV** - Format tabulaire standard
- 📊 **Excel** - Fichier .xlsx avec formatage
- 📋 **JSON** - Structure de données complète
- 🔖 **XML** - Format structuré
- 📕 **PDF** - Rapport professionnel avec images
- 🖼️ **ZIP Images** - Archive de toutes les images extraites

### 4. Notifications & Mode Asynchrone
- 🔔 Notification sonore à la fin du scraping
- 💬 Notifications browser (même hors de l'app)
- 📊 Barre de progression persistante
- 🌐 Navigation libre pendant le traitement
- ⏰ Mises à jour en temps réel

### 5. Sélection d'Export Avancée
- 🎚️ Slider pour choisir le nombre d'éléments
- ☑️ Sélection manuelle d'éléments spécifiques
- 📈 Aperçu du nombre d'éléments à exporter
- 🎯 Export de tous les sous-éléments (plus de "... et X autres")

## 🏗️ Architecture

```
scraper-pro/
├── backend/                 # Django REST API
│   ├── api/                # Endpoints REST
│   │   ├── models.py      # Modèles de données
│   │   ├── serializers.py # Sérialiseurs DRF
│   │   ├── views.py       # ViewSets et actions
│   │   └── urls.py        # Routing API
│   ├── config/            # Configuration Django
│   ├── src/
│   │   ├── core/          # Logique métier
│   │   │   ├── analyzer.py          # Analyse de sites
│   │   │   ├── scraper.py           # Moteur de scraping
│   │   │   ├── fetcher.py           # Récupération de pages
│   │   │   ├── content_detector.py  # Détection de contenu
│   │   │   ├── subdomain_finder.py  # Découverte sous-domaines
│   │   │   └── path_finder.py       # Crawling de chemins
│   │   └── api/
│   │       └── routes/    # Routes API organisées
│   └── tests/             # Tests unitaires et d'intégration
│
├── frontend/              # React + Vite
│   ├── src/
│   │   ├── assets/       # CSS et ressources
│   │   │   └── css/     # Styles par page
│   │   ├── components/   # Composants réutilisables
│   │   │   ├── NotificationCenter/  # Système de notifications
│   │   │   ├── ProgressLogs/        # Logs de progression
│   │   │   └── ContentSelector/     # Sélecteur de contenu
│   │   ├── contexts/     # React Context API
│   │   │   ├── AuthContext.jsx      # Authentification
│   │   │   └── ScrapingContext.jsx  # État de scraping async
│   │   ├── pages/        # Pages de l'application
│   │   │   ├── Landing/     # Page d'accueil
│   │   │   ├── Login/       # Authentification
│   │   │   ├── Register/    # Inscription
│   │   │   ├── Dashboard/   # Tableau de bord
│   │   │   ├── Analysis/    # Configuration du scraping
│   │   │   ├── Results/     # Résultats et export
│   │   │   ├── Reports/     # Rapports et statistiques
│   │   │   └── Settings/    # Paramètres utilisateur
│   │   └── services/     # API client
│   │       └── api.js    # Wrapper axios pour API
│   └── public/
│       └── sounds/       # Sons de notification
│
└── README.md             # Documentation principale
```

## 🚀 Installation

### Prérequis

- **Python 3.11+**
- **Node.js 18+**
- **npm ou yarn**
- **Git**

### 1. Cloner le Repository

```bash
git clone https://github.com/keizenx/conception_d-un_module_de_scrapping_configurable_intelligent.git
cd scraper-pro
```

### 2. Installation Backend (Django)

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données
python manage.py migrate

# Créer un superuser (optionnel)
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Le backend sera accessible sur `http://localhost:8000`

### 3. Installation Frontend (React)

```bash
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

### 4. Build Production

```bash
# Frontend
cd frontend
npm run build

# Les fichiers de production seront dans /dist
```

## ⚙️ Configuration

### Variables d'Environnement Backend

Créer un fichier `.env` dans `/backend`:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (par défaut SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# CORS (pour le développement)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Scraping
DEFAULT_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
MAX_DEPTH=3
DEFAULT_DELAY=500
REQUEST_TIMEOUT=30
```

### Configuration Frontend

Le fichier `/frontend/src/services/api.js` contient la configuration de l'API:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

Vous pouvez créer un fichier `.env` dans `/frontend`:

```env
VITE_API_URL=http://localhost:8000/api
```

## 📖 Utilisation

### 1. Lancer une Analyse

1. Accédez à la page **Analysis** (`/analysis`)
2. Entrez l'URL du site à analyser (ex: `https://example.com`)
3. Activez/désactivez l'inclusion des sous-domaines
4. Cliquez sur **"Analyser le site"**
5. L'analyse se fait en arrière-plan - vous pouvez naviguer librement
6. Une notification vous préviendra quand c'est terminé

### 2. Configurer le Scraping

1. Après l'analyse, sélectionnez les types de contenu à extraire :
   - 📌 Titres principaux
   - 📝 Paragraphes
   - 🔗 Liens
   - 🖼️ Images
   - 📋 Listes
   - etc.

2. Configurez les options avancées :
   - Profondeur de crawling (1-5)
   - Délai entre requêtes (ms)
   - User-Agent personnalisé
   - Timeout des requêtes

3. Ajoutez des sélecteurs CSS personnalisés (optionnel)

4. Cliquez sur **"Lancer le Scraping"**

### 3. Visualiser les Résultats

1. La page **Results** (`/results`) affiche tous les éléments extraits
2. Utilisez les filtres pour affiner la recherche
3. Prévisualisez les éléments en cliquant dessus
4. Sélectionnez des éléments spécifiques (checkboxes)

### 4. Exporter les Données

1. Cliquez sur un bouton d'export (CSV, Excel, JSON, PDF, etc.)
2. Un modal s'ouvre pour configurer l'export :
   - 🎚️ Utilisez le slider pour choisir le nombre d'éléments
   - ☑️ Ou cochez "Exporter uniquement les sélectionnés"
3. Cliquez sur **"Exporter"**
4. Le fichier est téléchargé automatiquement

### 5. Consulter le Dashboard

- **Sessions récentes** avec statut
- **Statistiques** (total sessions, éléments extraits, etc.)
- **Bouton "Résultats"** pour accès rapide
- **Actions rapides** (Nouvelle analyse, Rapports)

## 🛠️ Technologies

### Backend
- **Django 5.0** - Framework web Python
- **Django REST Framework** - API REST
- **BeautifulSoup4** - Parsing HTML
- **Requests** - Requêtes HTTP
- **Playwright** (optionnel) - Navigation browser automatisée
- **lxml** - Parsing XML rapide

### Frontend
- **React 18.3** - Framework UI
- **Vite** - Build tool ultra-rapide
- **React Router v6** - Navigation
- **jsPDF** - Génération PDF client-side
- **xlsx** - Export Excel

### Base de Données
- **SQLite** (développement)
- **PostgreSQL** (production recommandée)

## 📡 API Documentation

### Endpoints Principaux

#### Authentification
```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/user/
```

#### Analyse
```http
POST /api/analyze/
GET  /api/scraping/{id}/logs/
GET  /api/scraping/{id}/status/
GET  /api/scraping/{id}/results/
```

#### Scraping
```http
POST /api/scraping/start/
GET  /api/scraping/{id}/
GET  /api/scraping/
```

#### Résultats
```http
GET  /api/results/
GET  /api/results/{id}/
GET  /api/results/{id}/export/?type=csv&limit=100&item_ids=1,2,3
```

#### Dashboard
```http
GET  /api/dashboard/stats/
GET  /api/dashboard/recent_sessions/
GET  /api/dashboard/charts/
```

#### Rapports
```http
GET  /api/reports/
GET  /api/reports/stats/
```

### Exemple d'Appel API

```javascript
// Lancer une analyse
const response = await fetch('http://localhost:8000/api/analyze/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Token your-auth-token'
  },
  body: JSON.stringify({
    url: 'https://example.com',
    include_subdomains: false
  })
});

const data = await response.json();
console.log('Session ID:', data.session_id);
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment contribuer :

1. **Fork** le projet
2. Créez votre **branche feature** (`git checkout -b feature/AmazingFeature`)
3. **Committez** vos changements (`git commit -m 'Add some AmazingFeature'`)
4. **Push** vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

### Guidelines de Contribution

- Code propre et documenté
- Tests unitaires pour les nouvelles fonctionnalités
- Respecter les conventions de nommage
- Commentaires en français pour la cohérence

## 📝 Roadmap

- [ ] Support OAuth2 (Google, GitHub)
- [ ] Scraping planifié (cron jobs)
- [ ] API GraphQL
- [ ] Mode headless avec Playwright
- [ ] Support proxy rotation
- [ ] Machine Learning pour détection avancée
- [ ] Exports vers bases de données externes
- [ ] Webhooks pour notifications externes
- [ ] Mode collaboratif multi-utilisateurs

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**Keizenx** - [GitHub](https://github.com/keizenx)

## 🙏 Remerciements

- **Django** et **DRF** pour le backend robuste
- **React** et **Vite** pour l'interface moderne
- **BeautifulSoup** pour le parsing HTML efficace
- Communauté open-source pour les libraries utilisées

---

<div align="center">
  <strong>⭐ Si ce projet vous a aidé, n'hésitez pas à lui donner une étoile ! ⭐</strong>
</div>
