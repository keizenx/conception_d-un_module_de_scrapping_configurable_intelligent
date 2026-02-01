// src/pages/Dashboard/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/Sidebar';
import SmartInputBar from '../../components/SmartInputBar/SmartInputBar';
import '../../assets/css/dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [analyticsData, setAnalyticsData] = useState({
    successfulAnalyses: 245,
    elementsDetected: 14800,
    categoriesIdentified: 8.2,
    analysisTime: 2.3,
    accuracy: 96
  });

  const [recentAnalyses, setRecentAnalyses] = useState([
    {
      id: 1,
      name: 'Amazon Électronique',
      url: 'amazon.com/electronics',
      icon: 'fas fa-shopping-cart',
      elements: 148,
      detectedItems: ['Prix', 'Images', 'Descriptions', 'Avis'],
      date: 'Il y a 2h',
      status: 'success',
      statusText: 'Terminée'
    },
    {
      id: 2,
      name: 'GitHub Trending',
      url: 'github.com/trending',
      icon: 'fas fa-code',
      elements: 42,
      detectedItems: ['Répositories', 'Stars', 'Forks', 'Langages'],
      date: 'Il y a 5h',
      status: 'success',
      statusText: 'Terminée'
    },
    {
      id: 3,
      name: 'Blog Tech',
      url: 'techblog.example.com',
      icon: 'fas fa-newspaper',
      elements: 23,
      detectedItems: ['Articles', 'Dates', 'Auteurs', 'Catégories'],
      date: 'Hier',
      status: 'warning',
      statusText: 'Partielle'
    },
    {
      id: 4,
      name: 'E-commerce Fashion',
      url: 'fashionstore.com',
      icon: 'fas fa-tshirt',
      elements: 89,
      detectedItems: ['Produits', 'Prix', 'Tailles', 'Couleurs'],
      date: 'Il y a 2 jours',
      status: 'success',
      statusText: 'Terminée'
    }
  ]);

  const [activities, setActivities] = useState([
    {
      id: 1,
      type: 'success',
      icon: 'fas fa-check',
      title: 'Analyse Terminée',
      description: '"Amazon Électronique" : 148 éléments détectés',
      time: 'Il y a 2h',
      actions: ['Voir', 'Exporter']
    },
    {
      id: 2,
      type: 'info',
      icon: 'fas fa-lightbulb',
      title: 'Nouvelle Recommandation',
      description: 'Configurer la surveillance quotidienne des prix',
      time: 'Il y a 4h',
      actions: ['Configurer']
    },
    {
      id: 3,
      type: 'progress',
      icon: 'fas fa-sync-alt fa-spin',
      title: 'ANALYSE EN COURS',
      description: 'news.ycombinator.com : 65% complété',
      time: 'En ce moment',
      progress: 65
    },
    {
      id: 4,
      type: 'warning',
      icon: 'fas fa-exclamation-triangle',
      title: 'Structure Modifiée',
      description: 'github.com a mis à jour son design',
      time: 'Il y a 1 jour',
      actions: ['Re-analyser']
    }
  ]);

  // Fonction pour gérer l'analyse
  const handleAnalyze = (input, type) => {
    console.log('Starting analysis:', { input, type });
    
    // Naviguer vers la page d'analyse avec les paramètres
    navigate(`/analysis?input=${encodeURIComponent(input)}&type=${type}`);
  };

  // Fonction pour télécharger un rapport
  const downloadReport = (analysisId) => {
    console.log('Downloading report for analysis:', analysisId);
    // Simulation de téléchargement
    alert(`Téléchargement du rapport ${analysisId} démarré...`);
  };

  // Fonction pour voir les détails d'une analyse
  const viewAnalysisDetails = (analysisId) => {
    console.log('Viewing analysis details:', analysisId);
    navigate(`/results?analysis=${analysisId}`);
  };

  return (
    <div className="dashboard-container">
      <Sidebar />
      
      <main className="main-content">
        {/* Top Bar */}
        <header className="top-bar">
          <h2>Tableau de Bord</h2>
          <div className="top-bar-actions">
            <button 
              className="btn btn-primary" 
              onClick={() => navigate('/analysis')}
            >
              <i className="fas fa-plus"></i>
              Nouvelle Analyse
            </button>
            <button className="btn btn-secondary">
              <i className="fas fa-bell"></i>
              <span className="notification-count">3</span>
            </button>
          </div>
        </header>

        {/* Smart Input Section */}
        <section className="card highlight-card">
          <div className="card-header">
            <h3><i className="fas fa-search-plus"></i> Démarrer une nouvelle analyse</h3>
            <span className="card-subtitle">
              Notre scrapeur détectera automatiquement tous les éléments scrappables
            </span>
          </div>
          
          <SmartInputBar 
            onAnalyze={handleAnalyze}
            placeholder="Collez une URL, un sélecteur CSS ou du HTML brut..."
          />
          
          {/* <div className="analysis-tips">
            <div className="tip">
              <i className="fas fa-link"></i>
              <div>
                <strong>Pour les débutants :</strong> Collez simplement l'URL du site
              </div>
            </div>
            <div className="tip">
              <i className="fas fa-bullseye"></i>
              <div>
                <strong>Pour les experts :</strong> Utilisez les sélecteurs CSS pour cibler précisément
              </div>
            </div>
          </div> */}
        </section>

        {/* Analytics Summary */}
        <section className="data-summary">
          <div className="summary-card">
            <div className="summary-icon" style={{backgroundColor: '#e3f2fd'}}>
              <i className="fas fa-check-circle" style={{color: '#1976d2'}}></i>
            </div>
            <div className="summary-content">
              <h4>Analyses Réussies</h4>
              <p className="summary-number">
                {analyticsData.successfulAnalyses.toLocaleString()}
                <span className="summary-change positive">+32</span>
              </p>
              <p className="summary-label">Ce mois</p>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon" style={{backgroundColor: '#f3e5f5'}}>
              <i className="fas fa-bullseye" style={{color: '#7b1fa2'}}></i>
            </div>
            <div className="summary-content">
              <h4>Éléments Détectés</h4>
              <p className="summary-number">
                {analyticsData.elementsDetected.toLocaleString()}
              </p>
              <p className="summary-label">En moyenne par analyse</p>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon" style={{backgroundColor: '#e8f5e9'}}>
              <i className="fas fa-tags" style={{color: '#388e3c'}}></i>
            </div>
            <div className="summary-content">
              <h4>Catégories Identifiées</h4>
              <p className="summary-number">
                {analyticsData.categoriesIdentified}
              </p>
              <p className="summary-label">Catégories moyennes par site</p>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon" style={{backgroundColor: '#fff3e0'}}>
              <i className="fas fa-bolt" style={{color: '#f57c00'}}></i>
            </div>
            <div className="summary-content">
              <h4>Temps d'Analyse</h4>
              <p className="summary-number">
                {analyticsData.analysisTime}s
              </p>
              <p className="summary-label">Moyenne par site</p>
            </div>
          </div>

          <div className="summary-card">
            <div className="summary-icon" style={{backgroundColor: '#ffebee'}}>
              <i className="fas fa-crosshairs" style={{color: '#d32f2f'}}></i>
            </div>
            <div className="summary-content">
              <h4>Précision</h4>
              <p className="summary-number">
                {analyticsData.accuracy}%
              </p>
              <p className="summary-label">Des suggestions sont pertinentes</p>
            </div>
          </div>
        </section>

        {/* Recent Analyses */}
        <section className="card">
          <div className="card-header">
            <h3><i className="fas fa-history"></i> Analyses Récentes</h3>
            <Link to="/results" className="btn btn-small">
              <i className="fas fa-list"></i>
              Voir toutes
            </Link>
          </div>
          
          <table className="analyses-table">
            <thead>
              <tr>
                <th>SITE ANALYSÉ</th>
                <th>ÉLÉMENTS DÉTECTÉS</th>
                <th>DATE</th>
                <th>STATUT</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {recentAnalyses.map((analysis) => (
                <tr key={analysis.id}>
                  <td>
                    <div className="site-info">
                      <i className={analysis.icon}></i>
                      <div>
                        <strong>{analysis.name}</strong>
                        <small>{analysis.url}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="detected-elements">
                      <span className="element-count">{analysis.elements} éléments</span>
                      <div className="element-tags">
                        {analysis.detectedItems.slice(0, 3).map((item, index) => (
                          <span key={index} className="element-tag">{item}</span>
                        ))}
                        {analysis.detectedItems.length > 3 && (
                          <span className="element-tag more">+{analysis.detectedItems.length - 3}</span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td>{analysis.date}</td>
                  <td>
                    <span className={`status-badge ${analysis.status}`}>
                      {analysis.statusText}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button 
                        className="btn-icon" 
                        title="Voir l'analyse"
                        onClick={() => viewAnalysisDetails(analysis.id)}
                      >
                        <i className="fas fa-eye"></i>
                      </button>
                      <button 
                        className="btn-icon" 
                        title="Configurer le scraping"
                        onClick={() => navigate(`/analysis?from=${analysis.id}`)}
                      >
                        <i className="fas fa-cog"></i>
                      </button>
                      <button 
                        className="btn-icon" 
                        title="Exporter"
                        onClick={() => downloadReport(analysis.id)}
                      >
                        <i className="fas fa-download"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Activity Feed & Recommendations */}
        <div className="two-column-layout">
          {/* Activity Feed */}
          <section className="card">
            <div className="card-header">
              <h3><i className="fas fa-rss"></i> Activité Récente</h3>
            </div>
            <div className="activity-list">
              {activities.map((activity) => (
                <div className="activity-item" key={activity.id}>
                  <div className={`activity-icon ${activity.type}`}>
                    <i className={activity.icon}></i>
                  </div>
                  <div className="activity-content">
                    <h4>{activity.title}</h4>
                    <p className="activity-time">{activity.time}</p>
                    <p className="activity-description">{activity.description}</p>
                    
                    {activity.progress && (
                      <div className="progress-container">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{width: `${activity.progress}%`}}
                          ></div>
                        </div>
                        <span className="progress-text">{activity.progress}% complété</span>
                      </div>
                    )}
                    
                    {activity.actions && activity.actions.length > 0 && (
                      <div className="activity-actions">
                        {activity.actions.map((action, index) => (
                          <button key={index} className="btn-link">
                            {action}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Recommendations */}
          <section className="card">
            <div className="card-header">
              <h3><i className="fas fa-lightbulb"></i> Recommandations</h3>
            </div>
            <div className="recommendations">
              <div className="recommendation">
                <div className="rec-icon success">
                  <i className="fas fa-chart-line"></i>
                </div>
                <div className="rec-content">
                  <h4>Surveillance des prix</h4>
                  <p>Configurez une surveillance quotidienne des prix sur Amazon</p>
                  <button className="btn-link">Configurer</button>
                </div>
              </div>
              
              <div className="recommendation">
                <div className="rec-icon info">
                  <i className="fas fa-newspaper"></i>
                </div>
                <div className="rec-content">
                  <h4>Extraction d'articles</h4>
                  <p>Automatisez l'extraction des derniers articles tech</p>
                  <button className="btn-link">Automatiser</button>
                </div>
              </div>
              
              <div className="recommendation">
                <div className="rec-icon warning">
                  <i className="fas fa-sync-alt"></i>
                </div>
                <div className="rec-content">
                  <h4>Mise à jour nécessaire</h4>
                  <p>Re-analysez GitHub Trending pour nouvelles données</p>
                  <button className="btn-link">Re-analyser</button>
                </div>
              </div>
              
              <div className="recommendation">
                <div className="rec-icon primary">
                  <i className="fas fa-graduation-cap"></i>
                </div>
                <div className="rec-content">
                  <h4>Apprenez à scraper</h4>
                  <p>Suivez notre guide pour maîtriser les sélecteurs CSS</p>
                  <button className="btn-link">Voir le guide</button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;