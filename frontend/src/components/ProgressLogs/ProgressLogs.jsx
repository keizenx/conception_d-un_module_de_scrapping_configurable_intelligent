// Location: frontend/src/components/ProgressLogs/ProgressLogs.jsx
// Composant pour afficher les logs de progression en temps réel
// Affiche les messages pendant l'analyse d'un site
// RELEVANT FILES: Analysis.jsx, api.js, dashboard.css

import React, { useEffect, useState, useRef } from 'react';
import api from '../../services/api';
import './ProgressLogs.css';

const ProgressLogs = ({ sessionId, isActive, onAnalysisComplete }) => {
    const [logs, setLogs] = useState([]);
    const [currentStep, setCurrentStep] = useState('');
    const logsEndRef = useRef(null);
    const pollInterval = useRef(null);

    const scrollToBottom = () => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (!sessionId || !isActive) return;

        // Fonction pour récupérer les logs
        const fetchLogs = async () => {
            try {
                const data = await api.getSessionLogs(sessionId);
                setLogs(data.logs || []);
                setCurrentStep(data.current_step || '');
                
                // Si la session est terminée, récupérer les résultats
                if (data.status === 'completed' || data.status === 'failed') {
                    if (pollInterval.current) {
                        clearInterval(pollInterval.current);
                    }
                    
                    // Récupérer les résultats finaux
                    if (data.status === 'completed' && onAnalysisComplete) {
                        const results = await api.getSessionResults(sessionId);
                        onAnalysisComplete(results);
                    }
                }
            } catch (error) {
                console.error('Erreur lors de la récupération des logs:', error);
            }
        };

        // Récupérer immédiatement
        fetchLogs();

        // Puis récupérer toutes les 1 seconde
        pollInterval.current = setInterval(fetchLogs, 1000);

        return () => {
            if (pollInterval.current) {
                clearInterval(pollInterval.current);
            }
        };
    }, [sessionId, isActive, onAnalysisComplete]);

    useEffect(() => {
        scrollToBottom();
    }, [logs]);

    if (!sessionId || logs.length === 0) {
        return null;
    }

    return (
        <div className="progress-logs-container">
            <div className="progress-logs-header">
                <span className="material-icons">terminal</span>
                <h3>Progression de l'analyse</h3>
                {currentStep && (
                    <span className="current-step">
                        <span className="material-icons spinning">autorenew</span>
                        {currentStep}
                    </span>
                )}
            </div>
            <div className="progress-logs-content">
                {logs.map((log, index) => (
                    <div key={index} className={`log-entry log-${log.type || 'info'}`}>
                        <span className="log-timestamp">
                            {new Date(log.timestamp).toLocaleTimeString('fr-FR')}
                        </span>
                        <span className="log-message">{log.message}</span>
                    </div>
                ))}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
};

export default ProgressLogs;
