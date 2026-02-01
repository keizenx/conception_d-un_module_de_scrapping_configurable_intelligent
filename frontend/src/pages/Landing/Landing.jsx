import React from 'react';
import { Link } from 'react-router-dom';
import '../../assets/css/landing.css';

const Landing = () => {
  return (
    <div className="landing-container">
      <div className="hero-section">
        <div className="hero-content">
          <h1>Scraper Pro</h1>
          <p className="tagline">Solution Enterprise de Web Scraping Intelligent</p>
          <p className="description">
            Analysez, surveillez et extrayez des données web de manière intelligente et automatisée.
            Interface moderne, performances optimales, sécurité maximale.
          </p>
          <div className="hero-actions">
            <Link to="/dashboard" className="btn btn-primary">
              <i className="fas fa-chart-bar"></i>
              Accéder au Dashboard
            </Link>
            <Link to="/analysis" className="btn btn-secondary">
              <i className="fas fa-chart-line"></i>
              Voir les Analyses
            </Link>
          </div>
        </div>
        <div className="hero-visual">
          <div className="dashboard-preview">
            <div className="preview-header">
              <div className="preview-logo">Scraper Pro</div>
              <div className="preview-nav">
                <span>Dashboard</span>
                <span>Analysis</span>
                <span>Results</span>
              </div>
            </div>
            <div className="preview-content">
              <div className="preview-sidebar"></div>
              <div className="preview-main">
                <div className="preview-card">
                  <h3>Analyse de Site</h3>
                  <div className="preview-stats">
                    <div className="stat">142 Images</div>
                    <div className="stat">4 Sous-domaines</div>
                    <div className="stat">99.8% Succès</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2>Fonctionnalités Principales</h2>
        <div className="features-grid">
          <div className="feature-card">
            <i className="fas fa-search"></i>
            <h3>Analyse Intelligente</h3>
            <p>Détection automatique des structures DOM et adaptation en temps réel</p>
          </div>
          <div className="feature-card">
            <i className="fas fa-clock"></i>
            <h3>Surveillance Continue</h3>
            <p>Monitoring 24/7 avec alertes en temps réel</p>
          </div>
          <div className="feature-card">
            <i className="fas fa-shield-alt"></i>
            <h3>Sécurité Renforcée</h3>
            <p>Protection anti-détection et respect des politiques robots.txt</p>
          </div>
          <div className="feature-card">
            <i className="fas fa-chart-line"></i>
            <h3>Analyses Avancées</h3>
            <p>Graphiques interactifs et rapports détaillés</p>
          </div>
        </div>
      </div>

      <div className="cta-section">
        <h2>Prêt à commencer ?</h2>
        <p>Accédez à votre tableau de bord pour lancer votre première analyse</p>
        <Link to="/dashboard" className="btn btn-primary btn-large">
          <i className="fas fa-rocket"></i>
          Lancer Scraper Pro
        </Link>
      </div>
    </div>
  );
};

export default Landing;