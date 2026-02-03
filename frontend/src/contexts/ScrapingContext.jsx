// frontend/src/contexts/ScrapingContext.jsx
// Contexte pour gérer les tâches d'analyse et de scraping en arrière-plan
// Permet de naviguer librement pendant l'analyse et le scraping
// RELEVANT FILES: App.jsx, Analysis.jsx, api.js

import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import api from '../services/api';

const ScrapingContext = createContext(null);

// URL du son de notification
const NOTIFICATION_SOUND = '/sounds/notification.wav';

export const ScrapingProvider = ({ children }) => {
  // Liste des tâches en cours (analyse + scraping)
  const [activeTasks, setActiveTasks] = useState([]);
  // Notifications à afficher
  const [notifications, setNotifications] = useState([]);
  // Référence audio
  const audioRef = useRef(null);
  // Compteur pour limiter les sons
  const soundCountRef = useRef(0);
  const lastSoundTimeRef = useRef(0);
  // Set pour tracker les tâches déjà notifiées
  const notifiedTasksRef = useRef(new Set());
  
  // Charger le son
  useEffect(() => {
    audioRef.current = new Audio(NOTIFICATION_SOUND);
    audioRef.current.volume = 0.5;
  }, []);

  // Jouer le son de notification (limité à 2 fois par 10 secondes)
  const playNotificationSound = useCallback(() => {
    const now = Date.now();
    
    // Reset le compteur après 10 secondes
    if (now - lastSoundTimeRef.current > 10000) {
      soundCountRef.current = 0;
    }
    
    // Limiter à 2 sons maximum
    if (soundCountRef.current >= 2) {
      console.log('Son limité - déjà joué 2 fois');
      return;
    }
    
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(err => {
        console.log('Impossible de jouer le son:', err);
      });
      soundCountRef.current++;
      lastSoundTimeRef.current = now;
    }
  }, []);

  // Demander la permission pour les notifications browser
  const requestNotificationPermission = useCallback(async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  }, []);

  // Afficher une notification browser
  const showBrowserNotification = useCallback((title, body, icon = '⚡') => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body,
        icon: '/favicon.ico',
        badge: '/favicon.ico',
        tag: 'scraping-notification',
        requireInteraction: false,
      });
    }
  }, []);

  // Retirer une notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Ajouter une notification dans l'app
  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random(); // ID unique
    const newNotification = {
      id,
      ...notification,
      timestamp: new Date(),
    };
    
    console.log('Ajout notification:', newNotification);
    setNotifications(prev => {
      // Éviter les doublons de notifications similaires
      const isDuplicate = prev.some(n => 
        n.title === notification.title && 
        n.message === notification.message &&
        (Date.now() - new Date(n.timestamp).getTime()) < 5000
      );
      if (isDuplicate) {
        console.log('Notification dupliquée, ignorée');
        return prev;
      }
      return [...prev, newNotification];
    });
    
    // Jouer le son UNIQUEMENT pour success ou error (pas info)
    if (notification.type === 'success' || notification.type === 'error') {
      playNotificationSound();
      
      // Notification browser
      showBrowserNotification(
        notification.title,
        notification.message
      );
    }
    
    // Auto-remove après 15 secondes (plus long pour voir les notifs)
    setTimeout(() => {
      removeNotification(id);
    }, 15000);
    
    return id;
  }, [playNotificationSound, showBrowserNotification, removeNotification]);

  // ========== ANALYSE EN ARRIERE-PLAN ==========
  
  // Lancer une analyse en arrière-plan
  const startAnalysisTask = useCallback(async (url, includeSubdomains, onComplete) => {
    const taskId = Date.now();
    console.log('🚀 startAnalysisTask appelé - taskId:', taskId, 'url:', url);
    
    // Ajouter la tâche à la liste
    const task = {
      id: taskId,
      type: 'analysis',
      url,
      status: 'running',
      progress: 0,
      startedAt: new Date(),
      sessionId: null,
    };
    
    console.log('📝 Ajout tâche:', task);
    setActiveTasks(prev => {
      console.log('📊 activeTasks avant ajout:', prev);
      const newTasks = [...prev, task];
      console.log('📊 activeTasks après ajout:', newTasks);
      return newTasks;
    });
    
    // Notification de démarrage (silencieuse - pas de son)
    addNotification({
      type: 'info',
      title: '🔍 Analyse lancée',
      message: `Analyse de ${url} en cours...`,
    });

    try {
      // Lancer l'analyse
      console.log('🌐 Appel API analyzeURL...');
      const response = await api.analyzeURL(url, includeSubdomains);
      console.log('✅ Réponse API:', response);
      
      if (response.session_id) {
        // Mettre à jour la tâche avec l'ID de session
        setActiveTasks(prev => prev.map(t => 
          t.id === taskId 
            ? { ...t, sessionId: response.session_id, status: 'polling' }
            : t
        ));
        
        // Polling pour suivre la progression
        console.log('🔄 Démarrage polling pour session:', response.session_id);
        pollAnalysisStatus(taskId, response.session_id, onComplete);
      }
      
      return { taskId, sessionId: response.session_id };
      
    } catch (error) {
      console.error('❌ Erreur startAnalysisTask:', error);
      // Échec du lancement
      setActiveTasks(prev => prev.map(t => 
        t.id === taskId 
          ? { ...t, status: 'error', error: error.message }
          : t
      ));
      
      addNotification({
        type: 'error',
        title: '❌ Erreur d\'analyse',
        message: error.message || 'Impossible de lancer l\'analyse',
      });
      
      throw error;
    }
  }, [addNotification]);

  // Polling pour suivre le statut de l'analyse
  const pollAnalysisStatus = useCallback(async (taskId, sessionId, onComplete) => {
    const pollInterval = 1000; // 1 seconde
    const maxPolls = 300; // Max 5 minutes
    let polls = 0;
    
    const poll = async () => {
      console.log('Polling analyse - taskId:', taskId, 'sessionId:', sessionId, 'poll:', polls);
      
      try {
        const data = await api.getSessionLogs(sessionId);
        console.log('Polling analyse - data:', data);
        
        // Calculer la progression basée sur les logs
        const logs = data.logs || [];
        let progress = Math.min(logs.length * 10, 90); // Max 90% jusqu'à completion
        
        // Mettre à jour la progression
        setActiveTasks(prev => {
          console.log('Mise à jour activeTasks - prev:', prev);
          return prev.map(t => 
            t.id === taskId 
              ? { 
                  ...t, 
                  progress,
                  currentStep: data.current_step,
                  logs,
                }
              : t
          );
        });
        
        if (data.status === 'completed') {
          // Vérifier si on a déjà notifié cette tâche
          if (notifiedTasksRef.current.has(taskId)) {
            console.log('Tâche déjà notifiée, skip');
            return;
          }
          notifiedTasksRef.current.add(taskId);
          
          // Analyse terminée avec succès - récupérer les résultats
          const results = await api.getSessionResults(sessionId);
          
          setActiveTasks(prev => prev.map(t => 
            t.id === taskId 
              ? { ...t, status: 'completed', progress: 100, completedAt: new Date(), results }
              : t
          ));
          
          addNotification({
            type: 'success',
            title: '✅ Analyse terminée !',
            message: `${results.content_types?.length || 0} types de contenu détectés`,
            sessionId,
            taskType: 'analysis',
          });
          
          if (onComplete) {
            onComplete({ success: true, sessionId, results });
          }
          
          // Retirer de la liste après 30 secondes
          setTimeout(() => {
            setActiveTasks(prev => prev.filter(t => t.id !== taskId));
            notifiedTasksRef.current.delete(taskId);
          }, 30000);
          
          return;
        }
        
        if (data.status === 'failed') {
          // Analyse échouée
          setActiveTasks(prev => prev.map(t => 
            t.id === taskId 
              ? { ...t, status: 'error', error: 'Analyse échouée' }
              : t
          ));
          
          addNotification({
            type: 'error',
            title: '❌ Analyse échouée',
            message: 'Une erreur est survenue lors de l\'analyse',
          });
          
          if (onComplete) {
            onComplete({ success: false, error: 'Analyse échouée' });
          }
          
          return;
        }
        
        // Continuer le polling
        polls++;
        if (polls < maxPolls) {
          setTimeout(poll, pollInterval);
        } else {
          // Timeout
          addNotification({
            type: 'warning',
            title: '⏰ Timeout',
            message: 'L\'analyse prend trop de temps',
          });
        }
        
      } catch (error) {
        console.error('Erreur polling analyse:', error);
        polls++;
        if (polls < maxPolls) {
          setTimeout(poll, pollInterval);
        }
      }
    };
    
    // Démarrer le polling
    setTimeout(poll, pollInterval);
  }, [addNotification]);

  // ========== SCRAPING EN ARRIERE-PLAN ==========
  
  // Lancer un scraping en arrière-plan
  const startScrapingTask = useCallback(async (url, config, onComplete) => {
    const taskId = Date.now();
    
    // Ajouter la tâche à la liste
    const task = {
      id: taskId,
      type: 'scraping',
      url,
      config,
      status: 'running',
      progress: 0,
      startedAt: new Date(),
      sessionId: null,
    };
    
    setActiveTasks(prev => [...prev, task]);
    
    // Notification de démarrage
    addNotification({
      type: 'info',
      title: '🚀 Scraping lancé',
      message: `Extraction de ${url} en cours...`,
    });

    try {
      // Lancer le scraping - l'API attend la config complète
      const response = await api.startScraping(config);
      
      if (response.session_id) {
        // Mettre à jour la tâche avec l'ID de session
        setActiveTasks(prev => prev.map(t => 
          t.id === taskId 
            ? { ...t, sessionId: response.session_id, status: 'polling' }
            : t
        ));
        
        // Polling pour suivre la progression
        pollScrapingStatus(taskId, response.session_id, onComplete);
      }
      
      return { taskId, sessionId: response.session_id };
      
    } catch (error) {
      // Échec du lancement
      setActiveTasks(prev => prev.map(t => 
        t.id === taskId 
          ? { ...t, status: 'error', error: error.message }
          : t
      ));
      
      addNotification({
        type: 'error',
        title: '❌ Erreur de scraping',
        message: error.message || 'Impossible de lancer le scraping',
      });
      
      throw error;
    }
  }, [addNotification]);

  // Polling pour suivre le statut du scraping
  const pollScrapingStatus = useCallback(async (taskId, sessionId, onComplete) => {
    const pollInterval = 2000; // 2 secondes
    const maxPolls = 300; // Max 10 minutes
    let polls = 0;
    
    const poll = async () => {
      try {
        const status = await api.getScrapingStatus(sessionId);
        
        // Mettre à jour la progression
        setActiveTasks(prev => prev.map(t => 
          t.id === taskId 
            ? { 
                ...t, 
                progress: status.progress || 0,
                status: status.status,
                totalItems: status.total_items,
              }
            : t
        ));
        
        if (status.status === 'completed') {
          // Vérifier si on a déjà notifié cette tâche
          if (notifiedTasksRef.current.has(taskId)) {
            console.log('Scraping déjà notifié, skip');
            return;
          }
          notifiedTasksRef.current.add(taskId);
          
          // Scraping terminé avec succès
          setActiveTasks(prev => prev.map(t => 
            t.id === taskId 
              ? { ...t, status: 'completed', completedAt: new Date() }
              : t
          ));
          
          addNotification({
            type: 'success',
            title: '✅ Scraping terminé !',
            message: `${status.total_items || 0} éléments extraits`,
            sessionId,
          });
          
          if (onComplete) {
            onComplete({ success: true, sessionId, data: status });
          }
          
          // Retirer de la liste après 30 secondes
          setTimeout(() => {
            setActiveTasks(prev => prev.filter(t => t.id !== taskId));
            notifiedTasksRef.current.delete(taskId);
          }, 30000);
          
          return;
        }
        
        if (status.status === 'failed') {
          // Scraping échoué
          setActiveTasks(prev => prev.map(t => 
            t.id === taskId 
              ? { ...t, status: 'error', error: status.error }
              : t
          ));
          
          addNotification({
            type: 'error',
            title: '❌ Scraping échoué',
            message: status.error || 'Une erreur est survenue',
          });
          
          if (onComplete) {
            onComplete({ success: false, error: status.error });
          }
          
          return;
        }
        
        // Continuer le polling
        polls++;
        if (polls < maxPolls) {
          setTimeout(poll, pollInterval);
        } else {
          // Timeout
          addNotification({
            type: 'warning',
            title: '⏰ Timeout',
            message: 'Le scraping prend trop de temps',
          });
        }
        
      } catch (error) {
        console.error('Erreur polling:', error);
        polls++;
        if (polls < maxPolls) {
          setTimeout(poll, pollInterval);
        }
      }
    };
    
    // Démarrer le polling
    setTimeout(poll, pollInterval);
  }, [addNotification]);

  // Annuler une tâche
  const cancelTask = useCallback((taskId) => {
    setActiveTasks(prev => prev.filter(t => t.id !== taskId));
  }, []);

  // Vérifier si une tâche est en cours
  const isScrapingInProgress = activeTasks.some(t => 
    t.type === 'scraping' && (t.status === 'running' || t.status === 'polling')
  );
  
  const isAnalysisInProgress = activeTasks.some(t => 
    t.type === 'analysis' && (t.status === 'running' || t.status === 'polling')
  );
  
  // Récupérer une tâche d'analyse terminée par sessionId
  const getCompletedAnalysis = useCallback((sessionId) => {
    return activeTasks.find(t => 
      t.type === 'analysis' && 
      t.sessionId === sessionId && 
      t.status === 'completed'
    );
  }, [activeTasks]);

  // Demander la permission au chargement
  useEffect(() => {
    requestNotificationPermission();
  }, [requestNotificationPermission]);

  const value = {
    activeTasks,
    notifications,
    isScrapingInProgress,
    isAnalysisInProgress,
    startScrapingTask,
    startAnalysisTask,
    cancelTask,
    addNotification,
    removeNotification,
    playNotificationSound,
    getCompletedAnalysis,
  };

  return (
    <ScrapingContext.Provider value={value}>
      {children}
    </ScrapingContext.Provider>
  );
};

export const useScraping = () => {
  const context = useContext(ScrapingContext);
  if (!context) {
    throw new Error('useScraping must be used within a ScrapingProvider');
  }
  return context;
};

export default ScrapingContext;
