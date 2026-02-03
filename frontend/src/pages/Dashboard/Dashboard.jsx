// Location: frontend/src/pages/Dashboard/Dashboard.jsx
// Dashboard principal avec stats, graphiques et sessions récentes
// Page principale de l'application après connexion
// RELEVANT FILES: App.jsx, dashboard.css, AuthContext.jsx

import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Chart from 'chart.js/auto';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import '../../assets/css/dashboard.css';

const Dashboard = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    
    // State management
    const [stats, setStats] = useState({
        totalSessions: 0,
        extractedData: 0,
        successRate: 0,
        avgTime: '0s'
    });
    const [sessions, setSessions] = useState([]);
    const [activityData, setActivityData] = useState({
        labels: [],
        data: []
    });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    
    // Charger les statistiques du dashboard
    useEffect(() => {
        const loadDashboardData = async () => {
            try {
                setIsLoading(true);
                setError(null);
                
                // Charger les stats (séparément pour éviter que tout échoue si une requête échoue)
                try {
                    const statsData = await api.getDashboardStats();
                    setStats({
                        totalSessions: statsData.total_sessions || 0,
                        extractedData: statsData.extracted_data || 0,
                        successRate: statsData.success_rate || 0,
                        avgTime: statsData.avg_time || '0s'
                    });
                } catch (statsErr) {
                    console.error('Erreur stats:', statsErr);
                    // Si erreur 401, rediriger vers login
                    if (statsErr.message.includes('401') || statsErr.message.includes('authentifi')) {
                        await logout();
                        navigate('/login');
                        return;
                    }
                }
                
                // Charger les sessions récentes
                try {
                    const sessionsData = await api.getRecentSessions();
                    setSessions(sessionsData || []);
                } catch (sessionsErr) {
                    console.error('Erreur sessions:', sessionsErr);
                    setSessions([]);
                }
                
                // Charger les données d'activité pour le graphique
                try {
                    const activity = await api.getActivityData();
                    if (activity && activity.labels && activity.data) {
                        setActivityData({
                            labels: activity.labels,
                            data: activity.data
                        });
                    }
                } catch (activityErr) {
                    console.error('Erreur activity:', activityErr);
                }
                
            } catch (err) {
                console.error('Erreur lors du chargement des données:', err);
                setError(err.message || 'Erreur lors du chargement des données');
            } finally {
                setIsLoading(false);
            }
        };
        
        loadDashboardData();
    }, []);

    useEffect(() => {
        if (chartRef.current && activityData.labels.length > 0) {
            const ctx = chartRef.current.getContext('2d');
            
            // Gradient pour le fond du graphique
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(255, 77, 0, 0.3)');
            gradient.addColorStop(1, 'rgba(255, 77, 0, 0.0)');

            // Détruire l'ancien graphique si existant
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }

            // Créer le nouveau graphique avec les données de l'API
            chartInstance.current = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: activityData.labels,
                    datasets: [{
                        label: 'Sessions',
                        data: activityData.data,
                        borderColor: '#FF4D00',
                        backgroundColor: gradient,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#FF4D00',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
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
                            borderColor: '#FF4D00',
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

        // Cleanup
        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [activityData]);

    const handleNewScraping = () => {
        navigate('/analysis');
    };

    return (
        <div className="app-container">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
                    <div className="logo-icon"><span className="material-icons">flash_on</span></div>
                    SCRAPER PRO
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                {/* Header */}
                <header className="page-header">
                    <h1 className="page-title">Dashboard</h1>
                    <div className="header-actions">
                        <button className="btn-primary" onClick={handleNewScraping}>
                            <span className="material-icons">add</span>
                            Nouveau scraping
                        </button>
                        <div className="user-profile">
                            <div className="avatar">{user?.name?.substring(0, 2).toUpperCase() || 'U'}</div>
                            <span>{user?.name || 'Utilisateur'}</span>
                        </div>
                        <button className="btn-logout" onClick={async () => { await logout(); navigate('/login'); }}>
                            <span className="material-icons">logout</span>
                            Déconnexion
                        </button>
                    </div>
                </header>

                {/* Stats Grid */}
                {isLoading ? (
                    <div className="stats-grid">
                        <div className="stat-card"><div className="stat-value">Chargement...</div></div>
                        <div className="stat-card"><div className="stat-value">Chargement...</div></div>
                        <div className="stat-card"><div className="stat-value">Chargement...</div></div>
                        <div className="stat-card"><div className="stat-value">Chargement...</div></div>
                    </div>
                ) : (
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-header">
                                <div>
                                    <div className="stat-label">Sessions totales</div>
                                </div>
                                <div className="stat-icon"><span className="material-icons">rocket_launch</span></div>
                            </div>
                            <div className="stat-value">{stats.totalSessions.toLocaleString()}</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-header">
                                <div>
                                    <div className="stat-label">Données extraites</div>
                                </div>
                                <div className="stat-icon"><span className="material-icons">inventory_2</span></div>
                            </div>
                            <div className="stat-value">{stats.extractedData > 1000 ? `${(stats.extractedData / 1000).toFixed(1)}K` : stats.extractedData}</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-header">
                                <div>
                                    <div className="stat-label">Taux de succès</div>
                                </div>
                                <div className="stat-icon"><span className="material-icons">check_circle</span></div>
                            </div>
                            <div className="stat-value">{stats.successRate}%</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-header">
                                <div>
                                    <div className="stat-label">Temps moyen</div>
                                </div>
                                <div className="stat-icon"><span className="material-icons">flash_on</span></div>
                            </div>
                            <div className="stat-value">{stats.avgTime}</div>
                        </div>
                    </div>
                )}

                {/* Content Grid */}
                <div className="content-grid">
                    {/* Activity Chart */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Activité (7 derniers jours)</h3>
                            <span className="card-action">Voir tout →</span>
                        </div>
                        <div className="chart-container">
                            <canvas ref={chartRef} id="activityChart"></canvas>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Actions rapides</h3>
                        </div>
                        <div className="quick-actions">
                            <div className="quick-action-btn" onClick={() => navigate('/analysis')}>
                                <div className="action-icon"><span className="material-icons">search</span></div>
                                <div className="action-text">
                                    <h4>Analyser une URL</h4>
                                    <p>Configuration rapide</p>
                                </div>
                            </div>
                            <div className="quick-action-btn" onClick={() => navigate('/results')}>
                                <div className="action-icon results-icon"><span className="material-icons">visibility</span></div>
                                <div className="action-text">
                                    <h4>Voir les résultats</h4>
                                    <p>Dernière session</p>
                                </div>
                            </div>
                            <div className="quick-action-btn" onClick={() => navigate('/reports')}>
                                <div className="action-icon"><span className="material-icons">bar_chart</span></div>
                                <div className="action-text">
                                    <h4>Voir rapports</h4>
                                    <p>Historique complet</p>
                                </div>
                            </div>
                            <div className="quick-action-btn" onClick={() => navigate('/settings')}>
                                <div className="action-icon"><span className="material-icons">settings</span></div>
                                <div className="action-text">
                                    <h4>API Manager</h4>
                                    <p>Clés et webhooks</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Sessions */}
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Sessions récentes</h3>
                        <span className="card-action" onClick={() => navigate('/reports')} style={{cursor: 'pointer'}}>Historique complet →</span>
                    </div>
                    <div className="session-list">
                        {isLoading ? (
                            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-muted)'}}>Chargement des sessions...</div>
                        ) : error ? (
                            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--error)'}}>Erreur: {error}</div>
                        ) : sessions.length === 0 ? (
                            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-muted)'}}>
                                <p>Aucune session récente</p>
                                <button className="btn-primary" onClick={() => navigate('/analysis')} style={{marginTop: '1rem'}}>
                                    <span className="material-icons">add</span>
                                    Lancer un scraping
                                </button>
                            </div>
                        ) : (
                            sessions.map((session) => (
                                <div key={session.id} className="session-item">
                                    <div className="session-info">
                                        <div className={`session-status status-${session.status}`}></div>
                                        <div className="session-details">
                                            <h4>{session.url || 'Session'}</h4>
                                            <p>{new Date(session.started_at).toLocaleString('fr-FR')}</p>
                                        </div>
                                    </div>
                                    <div className="session-meta">
                                        <div className="session-count">{session.total_items || 0} éléments</div>
                                        <span className={`status-badge ${session.status === 'completed' ? 'success' : session.status === 'failed' ? 'error' : 'pending'}`}>
                                            {session.status === 'completed' ? 'Terminé' : session.status === 'failed' ? 'Échoué' : session.status === 'in_progress' ? 'En cours' : 'En attente'}
                                        </span>
                                        {session.status === 'completed' && (
                                            <button 
                                                className="btn-results"
                                                onClick={() => navigate(`/results?session=${session.id}`)}
                                                title="Voir les résultats"
                                            >
                                                <span className="material-icons">visibility</span>
                                                Résultats
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
