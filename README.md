# Scraper Pro

Plateforme de web scraping automatisée et intelligente, conçue pour extraire, analyser et exporter des données web de manière efficace.

## Table des Matières

- [Aperçu](#aperçu)
- [Fonctionnalités Principales](#fonctionnalités-principales)
- [Installation Facile](#installation-facile)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [License](#license)

## Aperçu

Scraper Pro est une solution clé en main pour le scraping de données. Elle combine une interface utilisateur intuitive avec un backend puissant capable de contourner les protections anti-bot modernes. Idéale pour les développeurs, data analysts et entreprises ayant besoin de collecter des données structurées.

### Points Clés

- **Installation Simplifiée** : Scripts et commandes prêts à l'emploi.
- **Analyse Intelligente** : Détection automatique des structures de données (produits, articles, contacts).
- **Contournement Anti-Bot** : Utilisation de Playwright en mode furtif pour scraper des sites complexes (ex: sites B2B, e-commerce).
- **Export Flexible** : Données disponibles en CSV, JSON, Excel, XML et rapports PDF complets.
- **Gestion des Médias** : Téléchargement automatique des images et vidéos.

## Fonctionnalités Principales

### 1. Analyse et Découverte
- Détection automatique des types de contenu sur une page.
- Estimation intelligente du nombre de pages à scraper.
- Découverte récursive des liens et sous-domaines.
- Système de "Mémoire de Chemins" pour suivre les nouveaux contenus.

### 2. Moteur de Scraping Avancé
- Support des sites dynamiques (React, Vue, Angular) via Playwright.
- Gestion des sessions et cookies pour les sites nécessitant une authentification.
- Mode "Stealth" pour éviter la détection et les CAPTCHAs.
- Support des proxies et rotation d'User-Agent.

### 3. Interface Utilisateur Moderne
- Tableau de bord complet avec statistiques en temps réel.
- Configuration visuelle du scraping sans code.
- Prévisualisation des données avant export.
- Notifications en temps réel de l'avancement des tâches.

### 4. Exports et Rapports
- Génération de rapports PDF détaillés avec galeries d'images.
- Export des données brutes en JSON/XML pour intégration API.
- Export tabulaire en CSV/Excel pour analyse.
- Création d'archives ZIP pour les médias téléchargés.

## Installation Facile

Suivez ces étapes pour installer Scraper Pro sur votre machine locale.

### Prérequis

- **Python 3.11+**
- **Node.js 18+**
- **Git**

### 1. Récupération du Projet

Clonez le dépôt sur votre machine :

```bash
git clone https://github.com/votre-username/scraper-pro.git
cd scraper-pro
```

### 2. Installation Automatisée (Recommandée)

**Backend (Python/Django) :**

Ouvrez un terminal dans le dossier `backend` :

```bash
cd backend
# Création de l'environnement virtuel
python -m venv venv

# Activation (Windows)
venv\Scripts\activate
# Activation (Mac/Linux)
# source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Installation des navigateurs Playwright
playwright install chromium

# Initialisation de la base de données
python manage.py migrate

# Démarrage du serveur
python manage.py runserver
```

Le serveur backend sera accessible sur `http://localhost:8000`.

**Frontend (React/Vite) :**

Ouvrez un nouveau terminal dans le dossier `frontend` :

```bash
cd frontend

# Installation des dépendances
npm install

# Démarrage du serveur de développement
npm run dev
```

L'application sera accessible sur `http://localhost:5173`.

## Utilisation

1.  **Ouvrez l'application** : Accédez à `http://localhost:5173` dans votre navigateur.
2.  **Nouvelle Analyse** : Entrez l'URL du site cible (ex: `https://exemple.com`).
3.  **Configuration** : Laissez l'IA détecter le contenu ou sélectionnez manuellement les types de données (Images, Textes, Produits...).
4.  **Lancement** : Cliquez sur "Lancer le scraping". Vous pouvez fermer l'onglet, le processus tourne en arrière-plan.
5.  **Résultats** : Une fois terminé, consultez les données, visualisez les galeries d'images et exportez vos fichiers.

## Architecture

Le projet est divisé en deux parties principales :

-   **Backend (`/backend`)** : API REST développée avec Django et Django REST Framework. Elle gère la logique de scraping, la base de données SQLite et les tâches asynchrones.
-   **Frontend (`/frontend`)** : Interface utilisateur réactive construite avec React et Vite. Elle communique avec l'API pour lancer les tâches et afficher les résultats.

## Technologies

-   **Backend** : Python, Django 5, Playwright (Scraping), BeautifulSoup4 (Parsing), Pandas (Data Processing).
-   **Frontend** : React 19, Vite, Chart.js (Visualisation), Axios (Requêtes API).
-   **Base de données** : SQLite (par défaut), compatible PostgreSQL.

## License

Ce projet est sous licence MIT. Libre à vous de l'utiliser et de le modifier pour vos besoins personnels ou professionnels.
