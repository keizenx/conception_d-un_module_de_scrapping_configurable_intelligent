// frontend/src/components/NotificationCenter/NotificationCenter.jsx
// Composant pour afficher les notifications et la barre de progression des tâches
// Affiche les notifications en toast et l'indicateur d'analyse/scraping en cours
// RELEVANT FILES: ScrapingContext.jsx, App.jsx, NotificationCenter.css

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useScraping } from '../../contexts/ScrapingContext';
import './NotificationCenter.css';

function NotificationCenter() {
  const navigate = useNavigate();
  const { 
    activeTasks, 
    notifications, 
    removeNotification,
    cancelTask,
  } = useScraping();

  // Debug - afficher l'état dans la console
  console.log('NotificationCenter - activeTasks:', activeTasks);
  console.log('NotificationCenter - notifications:', notifications);

  // Tâches en cours (running ou polling)
  const runningTasks = activeTasks.filter(t => 
    t.status === 'running' || t.status === 'polling'
  );
  
  // Séparer les tâches par type
  const analysisTasks = runningTasks.filter(t => t.type === 'analysis');
  const scrapingTasks = runningTasks.filter(t => t.type === 'scraping');

  // Obtenir le label selon le type de tâche
  const getTaskLabel = (task) => {
    if (task.type === 'analysis') {
      return `Analyse de ${task.url}`;
    }
    return `Scraping de ${task.url}`;
  };

  return (
    <>
      {/* Barre de progression globale pour les tâches en cours */}
      {runningTasks.length > 0 && (
        <div className="scraping-progress-bar">
          {runningTasks.map((task, index) => (
            <div key={task.id} className={`progress-item ${task.type}`}>
              <div className="progress-content">
                <div className="progress-icon">
                  <span className={`material-icons ${task.status === 'running' ? 'spin' : ''}`}>
                    {task.type === 'analysis' ? 'travel_explore' : 'autorenew'}
                  </span>
                </div>
                <div className="progress-info">
                  <span className="progress-title">
                    {task.type === 'analysis' ? 'Analyse en cours' : 'Scraping en cours'}
                  </span>
                  <span className="progress-url">
                    {task.url}
                  </span>
                  {task.currentStep && (
                    <span className="progress-step">
                      {task.currentStep}
                    </span>
                  )}
                </div>
                <div className="progress-actions">
                  {task.totalItems && task.type === 'scraping' && (
                    <span className="progress-count">
                      {task.totalItems} éléments
                    </span>
                  )}
                  {task.type === 'analysis' && (
                    <button 
                      className="progress-view-btn"
                      onClick={() => navigate('/analysis')}
                    >
                      Continuer
                    </button>
                  )}
                  {task.type === 'scraping' && task.sessionId && (
                    <button 
                      className="progress-view-btn"
                      onClick={() => navigate(`/results?session=${task.sessionId}`)}
                    >
                      Voir
                    </button>
                  )}
                </div>
              </div>
              <div className="progress-track">
                <div 
                  className="progress-fill" 
                  style={{ width: `${task.progress || 0}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Notifications toast */}
      <div className="notification-container">
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            className={`notification-toast notification-${notification.type}`}
          >
            <div className="notification-icon">
              {notification.type === 'success' && <span className="material-icons" style={{ color: 'var(--success)' }}>check_circle</span>}
              {notification.type === 'error' && <span className="material-icons" style={{ color: 'var(--error)' }}>error</span>}
              {notification.type === 'warning' && <span className="material-icons" style={{ color: 'var(--warning)' }}>warning</span>}
              {notification.type === 'info' && <span className="material-icons" style={{ color: 'var(--info)' }}>info</span>}
            </div>
            <div className="notification-content">
              <div className="notification-title">{notification.title}</div>
              <div className="notification-message">{notification.message}</div>
            </div>
            <div className="notification-actions">
              {notification.sessionId && notification.type === 'success' && notification.taskType === 'analysis' && (
                <button 
                  className="notification-action-btn"
                  onClick={() => {
                    navigate('/analysis');
                    removeNotification(notification.id);
                  }}
                >
                  Configurer le scraping
                </button>
              )}
              {notification.sessionId && notification.type === 'success' && notification.taskType !== 'analysis' && (
                <button 
                  className="notification-action-btn"
                  onClick={() => {
                    navigate(`/results?session=${notification.sessionId}`);
                    removeNotification(notification.id);
                  }}
                >
                  Voir les résultats
                </button>
              )}
              <button 
                className="notification-close"
                onClick={() => removeNotification(notification.id)}
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default NotificationCenter;
