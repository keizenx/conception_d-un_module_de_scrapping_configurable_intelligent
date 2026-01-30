# Répartition des Rôles - Projet Scraper Pro

## 🎨 Équipe Front-end (React)

### Koffi Ornella - Développeuse Front-end
**Mission principale :** Transformer les besoins fonctionnels en une interface utilisateur fluide, moderne et intuitive.

**Tâches spécifiques :**
1.  **Initialisation & Dashboard :** Créer la structure du projet React et concevoir le Dashboard principal. Il doit être épuré ("sans bruit") pour une lecture immédiate des métriques.
2.  **Pages Clés :** 
    *   **Analyse :** Interface pour configurer les nouveaux scrapings.
    *   **Résultats :** Tableaux dynamiques pour visualiser les données extraites.
    *   **Rapports :** Vue d'ensemble historique des sessions de scraping.
3.  **Barre d'entrée intelligente :** Implémenter le composant polyvalent acceptant une URL, un sélecteur CSS ou du HTML brut.
4.  **Sélecteur Visuel :** (Défi technique) Créer un système permettant de cliquer sur des éléments d'une page web (via iframe/proxy) pour générer automatiquement les sélecteurs CSS.
5.  **Export & UX :** Intégrer les boutons d'export (CSV/Excel/JSON) et gérer l'affichage des erreurs avec des messages clairs et des solutions de secours (fallback).

### Kouame Aka Richard - Product Owner (PO)
**Mission principale :** Garant de la vision produit et de la satisfaction utilisateur.

**Tâches spécifiques :**
1.  **Validation UI/UX :** Examiner chaque écran produit par Ornella pour s'assurer qu'il répond aux besoins métiers.

2.  **Cohérence :** S'assurer que le workflow (de l'URL au rapport final) est logique et sans friction.

---

## ⚙️ Équipe Back-end (Analyse & Scraping)

### Oumar Vivien - Développeur Back-end (Moteur)
**Mission principale :** Construire l'intelligence du scraper et l'API de communication.

**Tâches spécifiques :**
1.  **Architecture API :** Créer les routes REST (`/analyze`, `/scrape`, `/results`) pour que le Front-end puisse communiquer avec le moteur.
2.  **Moteur de décision :** Développer la logique qui analyse le HTML reçu et décide de la meilleure méthode d'extraction.
3.  **Fallback Intelligent :** Implémenter des algorithmes de secours si un sélecteur CSS devient obsolète ou si la structure du site change.

### Kouakou Jean Raphael - Développeur Back-end (Données & Rapports)
**Mission principale :** Gérer la persistance des données, les fichiers et le suivi des processus.

**Tâches spécifiques :**
1.  **Gestion des Statuts :** Mettre en place un système de suivi en temps réel (ex: via WebSockets ou polling) pour informer le front du statut (`en cours`, `terminé`, `bloqué`).
2.  **Stockage & Fichiers :** Gérer la base de données (configurations de scraping) et la génération physique des fichiers d'export (CSV, JSON, Excel).
3.  **Structuration des Rapports :** Transformer les données brutes du moteur d'Oumar en rapports structurés prêts à être affichés par Ornella.
