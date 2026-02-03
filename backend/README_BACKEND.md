# backend/README_BACKEND.md
# Documentation Backend SCRAPER PRO
# Guide de démarrage et documentation des routes API
# RELEVANT FILES: config/settings.py, api/urls.py, api/views.py, requirements.txt

## 🚀 Démarrage rapide

### Installation
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Créer la base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### Créer un superuser (admin)
```bash
python manage.py createsuperuser
```

### Lancer le serveur
```bash
python manage.py runserver
```

Le serveur démarre sur **http://localhost:8000**

---

## 📋 Routes API

### **Authentification** (`/api/auth/`)
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/logout/` - Déconnexion (auth requise)
- `GET /api/auth/me/` - Infos utilisateur (auth requise)

### **Analyse** (`/api/analysis/`)
- `POST /api/analysis/analyze/` - Analyser une URL avant scraping

### **Scraping** (`/api/scraping/`)
- `GET /api/scraping/` - Liste toutes les sessions
- `POST /api/scraping/` - Créer une nouvelle session
- `GET /api/scraping/{id}/` - Détails d'une session
- `PUT /api/scraping/{id}/` - Modifier une session
- `DELETE /api/scraping/{id}/` - Supprimer une session
- `POST /api/scraping/{id}/cancel/` - Annuler une session

### **Résultats** (`/api/results/`)
- `GET /api/results/` - Liste tous les résultats
- `GET /api/results/{id}/` - Détails d'un résultat
- `GET /api/results/by_session/?session_id=123` - Résultats par session

### **Rapports** (`/api/reports/`)
- `GET /api/reports/` - Liste tous les rapports
- `POST /api/reports/` - Créer un rapport
- `GET /api/reports/{id}/` - Détails d'un rapport
- `DELETE /api/reports/{id}/` - Supprimer un rapport
- `GET /api/reports/{id}/download/` - Télécharger un rapport

---

## 🔐 Authentification

Le backend utilise **Token Authentication** de Django REST Framework.

### Inscription
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "john",
  "email": "john@example.com",
  "password": "securepassword",
  "password_confirm": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "message": "Inscription réussie"
}
```

### Connexion
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "john",
  "password": "securepassword"
}
```

### Utiliser le token
Pour toutes les routes protégées, ajoute le header :
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

---

## 🕷️ Scraping

### Lancer un scraping
```bash
POST /api/scraping/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "url": "https://example.com",
  "configuration": {
    "max_pages": 5,
    "depth": 2,
    "selectors": {
      "title": "h1.product-title",
      "price": ".price"
    }
  }
}
```

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "user_name": "john",
  "url": "https://example.com",
  "status": "in_progress",
  "configuration": {...},
  "started_at": "2026-02-02T10:30:00Z",
  "total_items": 0,
  "success_count": 0,
  "error_count": 0
}
```

---

## 📊 Modèles de données

### User
- `username` - Nom d'utilisateur (unique)
- `email` - Email
- `password` - Mot de passe (hashé)
- `phone` - Téléphone (optionnel)
- `company` - Entreprise (optionnel)

### ScrapingSession
- `user` - Utilisateur (FK)
- `url` - URL à scraper
- `status` - Statut : pending, in_progress, completed, failed
- `configuration` - Config JSON
- `started_at` / `completed_at` - Timestamps
- `total_items` / `success_count` / `error_count` - Statistiques

### ScrapedData
- `session` - Session (FK)
- `data` - Données extraites (JSON)
- `element_type` - Type (product, article, etc.)
- `extracted_at` - Date d'extraction

### Report
- `session` - Session (FK)
- `user` - Utilisateur (FK)
- `title` - Titre du rapport
- `format` - Format : pdf, csv, excel, json
- `content` - Contenu JSON
- `file_path` - Chemin fichier

---

## ⚙️ Configuration

### CORS
Le backend accepte les requêtes depuis :
- `http://localhost:5173` (frontend Vite)
- `http://127.0.0.1:5173`

Pour ajouter d'autres origines, modifie `CORS_ALLOWED_ORIGINS` dans [config/settings.py](config/settings.py).

### Base de données
Par défaut : **SQLite** (`db.sqlite3`)

Pour changer (PostgreSQL, MySQL), modifie `DATABASES` dans settings.py.

---

## 🛠️ Développement

### Tests
```bash
python manage.py test
```

### Shell Django
```bash
python manage.py shell
```

### Admin Django
Accède à l'admin sur : **http://localhost:8000/admin**

---

## 📦 Dépendances

- **Django 5.1.6** - Framework web
- **Django REST Framework 3.15.2** - API REST
- **django-cors-headers 4.6.0** - Gestion CORS
- **BeautifulSoup4 4.12.3** - Parsing HTML
- **lxml 5.1.0** - Parser XML/HTML
- **Playwright 1.41.0** - Scraping dynamique

---

## 🔍 Debugging

### Voir les logs
Les logs s'affichent dans le terminal où tourne `runserver`.

### Browsable API
Django REST Framework fournit une interface web pour tester l'API :
- Ouvre http://localhost:8000/api/ dans ton navigateur
- Tu peux tester les endpoints directement

---

## 🚨 TODO

- [ ] Implémenter la logique de scraping asynchrone (Celery / RQ)
- [ ] Ajouter la génération de rapports PDF/CSV
- [ ] Ajouter pagination sur les résultats
- [ ] Implémenter rate limiting
- [ ] Ajouter tests unitaires
- [ ] Documenter avec Swagger/OpenAPI
