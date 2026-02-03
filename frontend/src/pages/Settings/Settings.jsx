// Location: frontend/src/pages/Settings/Settings.jsx
// Page de gestion des paramètres, API keys et webhooks
// Permet aux utilisateurs de gérer leurs clés API et webhooks
// RELEVANT FILES: dashboard.css, api.js, AuthContext.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import '../../assets/css/settings.css';

const Settings = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('api-keys');
    const [apiKeys, setApiKeys] = useState([]);
    const [webhooks, setWebhooks] = useState([]);
    const [showNewKeyModal, setShowNewKeyModal] = useState(false);
    const [showNewWebhookModal, setShowNewWebhookModal] = useState(false);
    const [newKeyName, setNewKeyName] = useState('');
    const [newWebhookUrl, setNewWebhookUrl] = useState('');
    const [newWebhookEvents, setNewWebhookEvents] = useState([]);

    useEffect(() => {
        loadApiKeys();
        loadWebhooks();
    }, []);

    const loadApiKeys = async () => {
        try {
            const data = await api.getApiKeys();
            setApiKeys(data);
        } catch (error) {
            console.error('Erreur chargement API keys:', error);
        }
    };

    const loadWebhooks = async () => {
        try {
            const data = await api.getWebhooks();
            setWebhooks(data);
        } catch (error) {
            console.error('Erreur chargement webhooks:', error);
        }
    };

    const handleCreateApiKey = async () => {
        if (!newKeyName.trim()) {
            alert('Veuillez entrer un nom pour la clé');
            return;
        }
        
        try {
            const newKey = await api.createApiKey({ name: newKeyName });
            setApiKeys([...apiKeys, newKey]);
            setShowNewKeyModal(false);
            setNewKeyName('');
            alert(`Clé créée: ${newKey.key}\n\nCopiez-la maintenant, elle ne sera plus affichée.`);
        } catch (error) {
            alert('Erreur création clé API');
        }
    };

    const handleDeleteApiKey = async (keyId) => {
        if (!confirm('Supprimer cette clé API ?')) return;
        
        try {
            await api.deleteApiKey(keyId);
            setApiKeys(apiKeys.filter(k => k.id !== keyId));
        } catch (error) {
            alert('Erreur suppression clé API');
        }
    };

    const handleCreateWebhook = async () => {
        if (!newWebhookUrl.trim()) {
            alert('Veuillez entrer une URL');
            return;
        }
        
        try {
            const newWebhook = await api.createWebhook({
                url: newWebhookUrl,
                events: newWebhookEvents
            });
            setWebhooks([...webhooks, newWebhook]);
            setShowNewWebhookModal(false);
            setNewWebhookUrl('');
            setNewWebhookEvents([]);
        } catch (error) {
            alert('Erreur création webhook');
        }
    };

    const handleDeleteWebhook = async (webhookId) => {
        if (!confirm('Supprimer ce webhook ?')) return;
        
        try {
            await api.deleteWebhook(webhookId);
            setWebhooks(webhooks.filter(w => w.id !== webhookId));
        } catch (error) {
            alert('Erreur suppression webhook');
        }
    };

    const toggleWebhookEvent = (event) => {
        if (newWebhookEvents.includes(event)) {
            setNewWebhookEvents(newWebhookEvents.filter(e => e !== event));
        } else {
            setNewWebhookEvents([...newWebhookEvents, event]);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert('Copié dans le presse-papier');
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
                    <h1 className="page-title">Paramètres</h1>
                    <div className="header-actions">
                        <button className="btn-secondary" onClick={() => navigate('/dashboard')}>
                            ← Retour
                        </button>
                    </div>
                </header>

                {/* Tabs */}
                <div className="settings-tabs">
                    <button 
                        className={`tab-btn ${activeTab === 'api-keys' ? 'active' : ''}`}
                        onClick={() => setActiveTab('api-keys')}
                    >
                        <span className="material-icons">vpn_key</span> Clés API
                    </button>
                    <button 
                        className={`tab-btn ${activeTab === 'webhooks' ? 'active' : ''}`}
                        onClick={() => setActiveTab('webhooks')}
                    >
                        <span className="material-icons">link</span> Webhooks
                    </button>
                    <button 
                        className={`tab-btn ${activeTab === 'general' ? 'active' : ''}`}
                        onClick={() => setActiveTab('general')}
                    >
                        <span className="material-icons">settings</span> Général
                    </button>
                </div>

                {/* API Keys Tab */}
                {activeTab === 'api-keys' && (
                    <div className="settings-section">
                        <div className="section-header">
                            <div>
                                <h2>Clés API</h2>
                                <p className="text-muted">Gérez vos clés d'authentification API</p>
                            </div>
                            <button className="btn-primary" onClick={() => setShowNewKeyModal(true)}>
                                + Nouvelle clé
                            </button>
                        </div>

                        <div className="api-keys-list">
                            {apiKeys.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-icon"><span className="material-icons md-48">vpn_key</span></div>
                                    <h3>Aucune clé API</h3>
                                    <p>Créez votre première clé pour commencer à utiliser l'API</p>
                                </div>
                            ) : (
                                apiKeys.map(key => (
                                    <div key={key.id} className="api-key-item">
                                        <div className="key-info">
                                            <h4>{key.name}</h4>
                                            <div className="key-value">
                                                <code>{key.key_prefix}••••••••••••••••</code>
                                                <button 
                                                    className="btn-icon"
                                                    onClick={() => copyToClipboard(key.key)}
                                                    title="Copier"
                                                >
                                                    <span className="material-icons">content_copy</span>
                                                </button>
                                            </div>
                                            <div className="key-meta">
                                                <span>Créée le {new Date(key.created_at).toLocaleDateString('fr-FR')}</span>
                                                <span>•</span>
                                                <span>Dernière utilisation: {key.last_used ? new Date(key.last_used).toLocaleDateString('fr-FR') : 'Jamais'}</span>
                                            </div>
                                        </div>
                                        <button 
                                            className="btn-danger-outline"
                                            onClick={() => handleDeleteApiKey(key.id)}
                                        >
                                            <span className="material-icons">delete</span> Supprimer
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* Webhooks Tab */}
                {activeTab === 'webhooks' && (
                    <div className="settings-section">
                        <div className="section-header">
                            <div>
                                <h2>Webhooks</h2>
                                <p className="text-muted">Recevez des notifications en temps réel</p>
                            </div>
                            <button className="btn-primary" onClick={() => setShowNewWebhookModal(true)}>
                                + Nouveau webhook
                            </button>
                        </div>

                        <div className="webhooks-list">
                            {webhooks.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-icon"><span className="material-icons md-48">link</span></div>
                                    <h3>Aucun webhook</h3>
                                    <p>Configurez des webhooks pour recevoir des notifications</p>
                                </div>
                            ) : (
                                webhooks.map(webhook => (
                                    <div key={webhook.id} className="webhook-item">
                                        <div className="webhook-info">
                                            <div className="webhook-url">
                                                <code>{webhook.url}</code>
                                                <span className={`webhook-status ${webhook.is_active ? 'active' : 'inactive'}`}>
                                                    {webhook.is_active ? <><span className="material-icons">check_circle</span> Actif</> : <><span className="material-icons">cancel</span> Inactif</>}
                                                </span>
                                            </div>
                                            <div className="webhook-events">
                                                {webhook.events.map(event => (
                                                    <span key={event} className="event-badge">{event}</span>
                                                ))}
                                            </div>
                                            <div className="webhook-meta">
                                                <span>Créé le {new Date(webhook.created_at).toLocaleDateString('fr-FR')}</span>
                                            </div>
                                        </div>
                                        <button 
                                            className="btn-danger-outline"
                                            onClick={() => handleDeleteWebhook(webhook.id)}
                                        >
                                            <span className="material-icons">delete</span> Supprimer
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}

                {/* General Tab */}
                {activeTab === 'general' && (
                    <div className="settings-section">
                        <h2>Paramètres généraux</h2>
                        <div className="settings-form">
                            <div className="form-group">
                                <label>Langue</label>
                                <select className="form-control">
                                    <option>Français</option>
                                    <option>English</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Format de date</label>
                                <select className="form-control">
                                    <option>JJ/MM/AAAA</option>
                                    <option>MM/JJ/AAAA</option>
                                    <option>AAAA-MM-JJ</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>
                                    <input type="checkbox" />
                                    <span>Activer les notifications email</span>
                                </label>
                            </div>
                            <button className="btn-primary">Enregistrer</button>
                        </div>
                    </div>
                )}
            </main>

            {/* New API Key Modal */}
            {showNewKeyModal && (
                <div className="modal-overlay" onClick={() => setShowNewKeyModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Nouvelle clé API</h3>
                        <div className="form-group">
                            <label>Nom de la clé</label>
                            <input 
                                type="text"
                                className="form-control"
                                placeholder="Ma clé API"
                                value={newKeyName}
                                onChange={(e) => setNewKeyName(e.target.value)}
                            />
                        </div>
                        <div className="modal-actions">
                            <button className="btn-secondary" onClick={() => setShowNewKeyModal(false)}>
                                Annuler
                            </button>
                            <button className="btn-primary" onClick={handleCreateApiKey}>
                                Créer
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* New Webhook Modal */}
            {showNewWebhookModal && (
                <div className="modal-overlay" onClick={() => setShowNewWebhookModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h3>Nouveau webhook</h3>
                        <div className="form-group">
                            <label>URL du webhook</label>
                            <input 
                                type="url"
                                className="form-control"
                                placeholder="https://example.com/webhook"
                                value={newWebhookUrl}
                                onChange={(e) => setNewWebhookUrl(e.target.value)}
                            />
                        </div>
                        <div className="form-group">
                            <label>Événements</label>
                            <div className="checkbox-group">
                                {['scraping.started', 'scraping.completed', 'scraping.failed', 'data.extracted'].map(event => (
                                    <label key={event}>
                                        <input 
                                            type="checkbox"
                                            checked={newWebhookEvents.includes(event)}
                                            onChange={() => toggleWebhookEvent(event)}
                                        />
                                        <span>{event}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                        <div className="modal-actions">
                            <button className="btn-secondary" onClick={() => setShowNewWebhookModal(false)}>
                                Annuler
                            </button>
                            <button className="btn-primary" onClick={handleCreateWebhook}>
                                Créer
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Settings;
