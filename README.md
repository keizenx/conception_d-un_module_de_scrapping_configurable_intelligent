# Structure du Projet - Scraper Pro

Voici l'organisation recommandée pour les dossiers du projet

##  Architecture Globale
```text
scraper-pro/
├── frontend/             # Projet React (Ornella & Richard)
├── backend/              # API & Moteur (Oumar & Raphael)
├── docs/                 # Documentation (Workflow, Rôles, etc.)
└── README.md             # Guide d'installation global
```

##  Frontend (React)
Structure suggérée pour Ornella :
```text
frontend/
├── public/               # Assets statiques
├── src/
│   ├── assets/           # Images, logos, icônes
│   ├── components/       # Composants réutilisables (Navbar, Sidebar, Button)
│   ├── pages/            # Écrans principaux
│   │   ├── Dashboard/
│   │   ├── Analysis/
│   │   ├── Results/
│   │   └── Reports/
│   ├── services/         # Appels API (Axios/Fetch)
│   ├── store/            # Gestion d'état (Redux/Context API)
│   ├── utils/            # Fonctions utilitaires
│   └── App.js            # Composant racine
└── package.json
```

##  Backend (Node.js/Express ou Python/FastAPI)
Structure suggérée pour Oumar et Raphael :
```text
backend/
├── src/
│   ├── api/              # Routes REST (Oumar)
│   │   ├── routes/
│   │   └── controllers/
│   ├── core/             # Moteur de scraping (Oumar)
│   │   ├── analyzer.js
│   │   └── scraper.js
│   ├── data/             # Gestion des données (Raphael)
│   │   ├── models/       # Modèles de base de données
│   │   └── storage/      # Logique de génération CSV/Excel
│   ├── utils/            # Helpers
│   └── index.js          # Point d'entrée
├── tests/                # Tests unitaires et d'intégration
└── package.json / requirements.txt
```
