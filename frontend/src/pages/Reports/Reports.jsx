// LOCATION: frontend/src/pages/Reports/Reports.jsx
// PURPOSE: Page des rapports avec statistiques, graphiques Chart.js, et historique des sessions
// WHY: Permet aux utilisateurs de visualiser l'historique complet de leurs sessions de scraping
// RELEVANT FILES: frontend/src/assets/css/reports.css, frontend/src/contexts/AuthContext.jsx

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Chart, registerables } from 'chart.js';
import api from '../../services/api';
import '../../assets/css/reports.css';

Chart.register(...registerables);

function Reports() {
  const navigate = useNavigate();
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  
  const [activeFilter, setActiveFilter] = useState('30 jours');
  const [activeTab, setActiveTab] = useState('Sessions');
  
  // State pour les données de l'API
  const [reports, setReports] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [stats, setStats] = useState({
    total_sessions: 0,
    total_elements: 0,
    success_rate: 0,
    error_rate: 0,
    avg_time: '0s'
  });
  const [chartData, setChartData] = useState({
    labels: [],
    sessions: [],
    elements: []
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Charger les rapports depuis l'API
  useEffect(() => {
    const loadReports = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const filters = {
          period: activeFilter
        };
        
        const data = await api.getReports(filters);
        setReports(data.reports || []);
        setSessions(data.sessions || []);
        setStats(data.stats || {
          total_sessions: 0,
          total_elements: 0,
          success_rate: 0,
          error_rate: 0,
          avg_time: '0s'
        });
        setChartData(data.chart || {
          labels: [],
          sessions: [],
          elements: []
        });
        
      } catch (err) {
        console.error('Erreur lors du chargement des rapports:', err);
        setError(err.message || 'Erreur lors du chargement des rapports');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadReports();
  }, [activeFilter]);

  // Initialiser le graphique
  useEffect(() => {
    if (chartRef.current && chartData.labels.length > 0) {
      const ctx = chartRef.current.getContext('2d');
      
      // Détruire l'ancien graphique
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      // Gradient
      const gradient = ctx.createLinearGradient(0, 0, 0, 350);
      gradient.addColorStop(0, 'rgba(255, 77, 0, 0.3)');
      gradient.addColorStop(1, 'rgba(255, 77, 0, 0.0)');
      
      // Choisir les données selon l'onglet actif
      let dataToShow = chartData.sessions;
      let labelText = 'Sessions';
      let color = '#FF4D00';
      
      if (activeTab === 'Éléments') {
        dataToShow = chartData.elements;
        labelText = 'Éléments extraits';
        color = '#00E5FF';
      } else if (activeTab === 'Succès') {
        // Calculer le taux de succès par jour (simulé)
        dataToShow = chartData.sessions.map(() => stats.success_rate);
        labelText = 'Taux de succès (%)';
        color = '#00FF88';
      }

      chartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: chartData.labels,
          datasets: [{
            label: labelText,
            data: dataToShow,
            borderColor: color,
            backgroundColor: gradient,
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: color,
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: '#141419',
              borderColor: color,
              borderWidth: 1,
              titleColor: '#FFFFFF',
              bodyColor: '#A0A0B0',
              padding: 12,
              displayColors: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: 'rgba(255, 77, 0, 0.1)',
                drawBorder: false
              },
              ticks: {
                color: '#606070'
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                color: '#606070'
              }
            }
          }
        }
      });
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [chartData, activeTab, stats.success_rate]);

  const handleDownload = async (reportId, format = 'json') => {
    try {
      const blob = await api.downloadReport(reportId, format);
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${reportId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Erreur lors du téléchargement:', error);
      alert(`Erreur lors du téléchargement du rapport: ${error.message || 'Erreur inconnue'}`);
    }
  };

  const handleViewDetails = (reportId) => {
    // Extraire l'ID numérique du format #SCR-XXXX
    const id = reportId.replace('#SCR-', '');
    navigate(`/results?session=${id}`);
  };

  const handleExport = (format) => {
    console.log('Export en format:', format);
    alert(`Export ${format} lancé ! Préparation du rapport...`);
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <div className="logo-icon">⚡</div>
          SCRAPER PRO
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="page-header">
          <h1 className="page-title">Rapports & Historique</h1>
          <div className="date-filter">
            {['7 jours', '30 jours', '90 jours', 'Tout'].map(filter => (
              <button
                key={filter}
                className={`date-btn ${activeFilter === filter ? 'active' : ''}`}
                onClick={() => setActiveFilter(filter)}
              >
                {filter}
              </button>
            ))}
          </div>
        </header>

        {/* Summary Grid */}
        <div className="summary-grid">
          <div className="summary-card">
            <div className="summary-icon">📦</div>
            <div className="summary-value">{stats.total_sessions}</div>
            <div className="summary-label">Sessions totales</div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">🎯</div>
            <div className="summary-value">{stats.total_elements > 1000 ? `${(stats.total_elements / 1000).toFixed(1)}K` : stats.total_elements}</div>
            <div className="summary-label">Éléments extraits</div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">✅</div>
            <div className="summary-value">{stats.success_rate}%</div>
            <div className="summary-label">Taux de succès moyen</div>
          </div>

          <div className="summary-card">
            <div className="summary-icon">⏱️</div>
            <div className="summary-value">{stats.avg_time}</div>
            <div className="summary-label">Temps moyen</div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="charts-grid">
          {/* Activity Timeline */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <span>📊</span>
                Activité sur 30 jours
              </h3>
              <div className="chart-tabs">
                {['Sessions', 'Éléments', 'Succès'].map(tab => (
                  <button
                    key={tab}
                    className={`chart-tab ${activeTab === tab ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
            <div className="chart-container">
              <canvas ref={chartRef} id="activityChart"></canvas>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <span>📊</span>
                Métriques de performance
              </h3>
            </div>
            <div className="metrics-list">
              <div className="metric-item">
                <div className="metric-header">
                  <span className="metric-label">Taux de succès</span>
                  <span className="metric-value" style={{ color: 'var(--success)' }}>{stats.success_rate}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${stats.success_rate}%` }}></div>
                </div>
              </div>

              <div className="metric-item">
                <div className="metric-header">
                  <span className="metric-label">Vitesse moyenne</span>
                  <span className="metric-value" style={{ color: 'var(--accent)' }}>{stats.avg_time}</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: '75%', background: 'linear-gradient(90deg, var(--accent), var(--primary))' }}></div>
                </div>
              </div>

              <div className="metric-item">
                <div className="metric-header">
                  <span className="metric-label">Taux d'erreur</span>
                  <span className="metric-value" style={{ color: 'var(--warning)' }}>{stats.error_rate}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${stats.error_rate}%`, background: 'linear-gradient(90deg, var(--warning), var(--error))' }}></div>
                </div>
              </div>

              <div className="metric-item">
                <div className="metric-header">
                  <span className="metric-label">Sessions complétées</span>
                  <span className="metric-value" style={{ color: 'var(--success)' }}>{stats.completed_sessions || 0}</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${stats.success_rate}%` }}></div>
                </div>
              </div>

              <div className="metric-item">
                <div className="metric-header">
                  <span className="metric-label">Sessions échouées</span>
                  <span className="metric-value" style={{ color: 'var(--error)' }}>{stats.failed_sessions || 0}</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: '0%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Session History */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <span>📜</span>
              Historique des sessions
            </h3>
          </div>

          <table className="history-table">
            <thead>
              <tr>
                <th>Session</th>
                <th>URL</th>
                <th>Statut</th>
                <th>Éléments</th>
                <th>Durée</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>
                    <div style={{color: 'var(--text-muted)'}}>Chargement des données...</div>
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>
                    <div style={{color: 'var(--error)'}}>Erreur: {error}</div>
                  </td>
                </tr>
              ) : sessions.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{textAlign: 'center', padding: '2rem'}}>
                    <div style={{color: 'var(--text-muted)'}}>Aucune session disponible</div>
                    <button 
                      className="btn-primary" 
                      onClick={() => navigate('/analysis')} 
                      style={{marginTop: '1rem'}}
                    >
                      Lancer un scraping
                    </button>
                  </td>
                </tr>
              ) : (
                sessions.map(session => (
                  <tr key={session.id}>
                    <td className="session-id">#{session.id}</td>
                    <td>
                      <div className="session-url" title={session.url}>
                        {session.url?.length > 40 ? session.url.substring(0, 40) + '...' : session.url}
                      </div>
                    </td>
                    <td>
                      <span className={`status-indicator status-${session.status}`}>
                        {session.status === 'completed' ? '✅ Terminé' : 
                         session.status === 'failed' ? '❌ Échoué' : 
                         session.status === 'in_progress' ? '⏳ En cours' : '⏸️ En attente'}
                      </span>
                    </td>
                    <td><span className="items-count">{session.total_items}</span></td>
                    <td><span className="duration-badge">{session.duration}</span></td>
                    <td>{session.started_at ? new Date(session.started_at).toLocaleDateString('fr-FR') : '-'}</td>
                    <td>
                      <div className="action-buttons">
                        {session.status === 'completed' && (
                          <>
                            <button 
                              className="action-btn view-btn"
                              onClick={() => navigate(`/results?session=${session.id}`)}
                              title="Voir les résultats"
                            >
                              👁️
                            </button>
                            <button 
                              className="action-btn download-btn"
                              onClick={() => handleViewDetails(`#SCR-${session.id}`)}
                              title="Exporter"
                            >
                              💾
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Export Section */}
        <div className="export-section">
          <div className="export-header">
            <h3 className="card-title">
              <span>💾</span>
              Exporter les rapports
            </h3>
          </div>

          <div className="export-options">
            <div className="export-card" onClick={() => handleExport('CSV')}>
              <div className="export-icon">📄</div>
              <h4>CSV Export</h4>
              <p>Format tableur universel</p>
            </div>

            <div className="export-card" onClick={() => handleExport('Excel')}>
              <div className="export-icon">📊</div>
              <h4>Excel Export</h4>
              <p>Avec graphiques et mise en forme</p>
            </div>

            <div className="export-card" onClick={() => handleExport('JSON')}>
              <div className="export-icon">🔧</div>
              <h4>JSON Export</h4>
              <p>Données structurées pour APIs</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Reports;
