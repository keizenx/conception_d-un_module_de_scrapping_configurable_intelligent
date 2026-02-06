// Location: frontend/src/pages/Profile/Profile.jsx
// Page de profil utilisateur avec édition des informations
// Permet de modifier nom, email, mot de passe, avatar et autres paramètres
// RELEVANT FILES: AuthContext.jsx, api.js, profile.css, Dashboard.jsx

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import '../../assets/css/profile.css';

const Profile = () => {
    const navigate = useNavigate();
    const { user, updateUser, logout } = useAuth();
    const fileInputRef = useRef(null);
    
    // States pour l'édition du profil
    const [isEditing, setIsEditing] = useState(false);
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
    
    // 2FA
    const [is2FAEnabled, setIs2FAEnabled] = useState(false);
    const [isToggling2FA, setIsToggling2FA] = useState(false);

    // Avatar
    const [avatarUrl, setAvatarUrl] = useState(null);
    
    // Form data
    const [formData, setFormData] = useState({
        name: user?.name || '',
        email: user?.email || '',
        bio: user?.bio || '',
        company: user?.company || '',
        role: user?.role || 'user'
    });
    
    // Password change data
    const [passwordData, setPasswordData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });
    
    // Messages
    const [message, setMessage] = useState({ type: '', text: '' });
    const [passwordMessage, setPasswordMessage] = useState({ type: '', text: '' });
    
    // Stats utilisateur
    const [userStats, setUserStats] = useState({
        totalSessions: 0,
        dataExtracted: 0,
        memberSince: '',
        lastLogin: ''
    });

    useEffect(() => {
        loadUserProfile();
    }, []);

    const loadUserProfile = async () => {
        try {
            const profile = await api.getUserProfile();
            console.log('Profile data reçu:', profile);
            
            setFormData({
                name: profile.name || '',
                email: profile.email || '',
                bio: profile.bio || '',
                company: profile.company || '',
                role: profile.role || 'user'
            });
            
            // Avatar
            setAvatarUrl(profile.avatar_url || null);
            
            // 2FA
            setIs2FAEnabled(profile.is_2fa_enabled || false);

            setUserStats({
                totalSessions: profile.total_sessions || 0,
                dataExtracted: profile.data_extracted || 0,
                memberSince: profile.member_since || 'Non défini',
                lastLogin: profile.last_login || 'Jamais'
            });
        } catch (error) {
            console.error('Erreur lors du chargement du profil:', error);
            // Définir des valeurs par défaut en cas d'erreur
            setUserStats({
                totalSessions: 0,
                dataExtracted: 0,
                memberSince: 'Erreur de chargement',
                lastLogin: 'Erreur de chargement'
            });
        }
    };

    // Gestion de l'avatar
    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    const handleAvatarChange = async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        
        // Validation côté client
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            setMessage({ type: 'error', text: 'Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WebP.' });
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            setMessage({ type: 'error', text: 'Le fichier est trop volumineux. Maximum 5 Mo.' });
            return;
        }
        
        setIsUploadingAvatar(true);
        setMessage({ type: '', text: '' });
        
        try {
            const result = await api.uploadAvatar(file);
            setAvatarUrl(result.avatar_url);
            setMessage({ type: 'success', text: 'Photo de profil mise à jour!' });
            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Erreur lors de l\'upload' });
        } finally {
            setIsUploadingAvatar(false);
        }
    };

    const handleDeleteAvatar = async () => {
        if (!avatarUrl) return;
        
        const confirmed = window.confirm('Supprimer votre photo de profil ?');
        if (!confirmed) return;
        
        setIsUploadingAvatar(true);
        
        try {
            await api.deleteAvatar();
            setAvatarUrl(null);
            setMessage({ type: 'success', text: 'Photo de profil supprimée' });
            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Erreur lors de la suppression' });
        } finally {
            setIsUploadingAvatar(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handlePasswordChange = (e) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSaveProfile = async () => {
        setIsSaving(true);
        setMessage({ type: '', text: '' });
        
        try {
            const updatedUser = await api.updateUserProfile(formData);
            
            // Mettre à jour le contexte d'authentification
            if (updateUser) {
                updateUser(updatedUser);
            }
            
            setMessage({ type: 'success', text: 'Profil mis à jour avec succès!' });
            setIsEditing(false);
            
            // Effacer le message après 3 secondes
            setTimeout(() => setMessage({ type: '', text: '' }), 3000);
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Erreur lors de la mise à jour' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleChangePassword = async () => {
        setPasswordMessage({ type: '', text: '' });
        
        // Validation
        if (!passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword) {
            setPasswordMessage({ type: 'error', text: 'Tous les champs sont requis' });
            return;
        }
        
        if (passwordData.newPassword !== passwordData.confirmPassword) {
            setPasswordMessage({ type: 'error', text: 'Les mots de passe ne correspondent pas' });
            return;
        }
        
        if (passwordData.newPassword.length < 8) {
            setPasswordMessage({ type: 'error', text: 'Le mot de passe doit contenir au moins 8 caractères' });
            return;
        }
        
        setIsSaving(true);
        
        try {
            await api.changePassword(passwordData.currentPassword, passwordData.newPassword);
            
            setPasswordMessage({ type: 'success', text: 'Mot de passe modifié avec succès!' });
            setPasswordData({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            });
            setIsChangingPassword(false);
            
            // Effacer le message après 3 secondes
            setTimeout(() => setPasswordMessage({ type: '', text: '' }), 3000);
        } catch (error) {
            setPasswordMessage({ type: 'error', text: error.message || 'Mot de passe actuel incorrect' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleToggle2FA = async () => {
        setIsToggling2FA(true);
        setPasswordMessage({ type: '', text: '' });
        
        try {
            if (is2FAEnabled) {
                await api.disable2FA();
                setIs2FAEnabled(false);
                setPasswordMessage({ type: 'success', text: 'Authentification à deux facteurs désactivée' });
            } else {
                await api.enable2FA();
                setIs2FAEnabled(true);
                setPasswordMessage({ type: 'success', text: 'Authentification à deux facteurs activée' });
            }
        } catch (error) {
            setPasswordMessage({ type: 'error', text: error.message || 'Erreur lors du changement 2FA' });
        } finally {
            setIsToggling2FA(false);
            setTimeout(() => setPasswordMessage({ type: '', text: '' }), 3000);
        }
    };

    const handleDeleteAccount = async () => {
        const confirmed = window.confirm(
            '⚠️ ATTENTION: Cette action est irréversible!\n\n' +
            'Toutes vos données seront définitivement supprimées:\n' +
            '- Sessions de scraping\n' +
            '- Résultats extraits\n' +
            '- Historique complet\n\n' +
            'Êtes-vous absolument sûr de vouloir supprimer votre compte?'
        );
        
        if (!confirmed) return;
        
        const doubleConfirm = window.confirm(
            'Dernière confirmation: Tapez OK pour supprimer définitivement votre compte'
        );
        
        if (!doubleConfirm) return;
        
        try {
            await api.deleteUserAccount();
            await logout();
            navigate('/');
        } catch (error) {
            setMessage({ type: 'error', text: error.message || 'Erreur lors de la suppression' });
        }
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
                    <div className="header-left">
                        <button className="btn-back" onClick={() => navigate('/dashboard')}>
                            <span className="material-icons">arrow_back</span>
                        </button>
                        <h1 className="page-title">Mon Profil</h1>
                    </div>
                    <div className="header-actions">
                        <button className="btn-logout" onClick={async () => { await logout(); navigate('/login'); }}>
                            <span className="material-icons">logout</span>
                            Déconnexion
                        </button>
                    </div>
                </header>

                {/* Profile Content */}
                <div className="profile-container">
                    {/* Profile Header Card */}
                    <div className="profile-header-card">
                        <div className="profile-avatar-section">
                            <div className="profile-avatar-wrapper">
                                <div 
                                    className={`profile-avatar-large ${isUploadingAvatar ? 'uploading' : ''}`}
                                    onClick={handleAvatarClick}
                                    title="Cliquez pour changer la photo"
                                >
                                    {avatarUrl ? (
                                        <img src={avatarUrl} alt="Avatar" className="avatar-image" />
                                    ) : (
                                        formData.name.substring(0, 2).toUpperCase() || 'U'
                                    )}
                                    <div className="avatar-overlay">
                                        <span className="material-icons">
                                            {isUploadingAvatar ? 'hourglass_empty' : 'camera_alt'}
                                        </span>
                                    </div>
                                </div>
                                {avatarUrl && (
                                    <button 
                                        className="btn-delete-avatar"
                                        onClick={handleDeleteAvatar}
                                        title="Supprimer la photo"
                                        disabled={isUploadingAvatar}
                                    >
                                        <span className="material-icons">close</span>
                                    </button>
                                )}
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleAvatarChange}
                                    accept="image/jpeg,image/png,image/gif,image/webp"
                                    style={{ display: 'none' }}
                                />
                            </div>
                            <div className="profile-header-info">
                                <h2>{formData.name}</h2>
                                <p className="profile-email">{formData.email}</p>
                                <span className="profile-role-badge">{formData.role === 'admin' ? 'Administrateur' : 'Utilisateur'}</span>
                            </div>
                        </div>
                        <div className="profile-stats-mini">
                            <div className="stat-mini">
                                <span className="material-icons">rocket_launch</span>
                                <div>
                                    <div className="stat-mini-value">{userStats.totalSessions}</div>
                                    <div className="stat-mini-label">Sessions</div>
                                </div>
                            </div>
                            <div className="stat-mini">
                                <span className="material-icons">inventory_2</span>
                                <div>
                                    <div className="stat-mini-value">{userStats.dataExtracted > 1000 ? `${(userStats.dataExtracted / 1000).toFixed(1)}K` : userStats.dataExtracted}</div>
                                    <div className="stat-mini-label">Données</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Messages */}
                    {message.text && (
                        <div className={`message-box ${message.type}`}>
                            <span className="material-icons">
                                {message.type === 'success' ? 'check_circle' : 'error'}
                            </span>
                            <span>{message.text}</span>
                        </div>
                    )}

                    {/* Profile Information Card */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">
                                <span className="material-icons">person</span>
                                Informations personnelles
                            </h3>
                            {!isEditing && (
                                <button className="btn-edit" onClick={() => setIsEditing(true)}>
                                    <span className="material-icons">edit</span>
                                    Modifier
                                </button>
                            )}
                        </div>
                        <div className="card-body">
                            <div className="form-grid">
                                <div className="form-group">
                                    <label>Nom complet</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        disabled={!isEditing}
                                        className="form-input"
                                        placeholder="Votre nom"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        disabled={!isEditing}
                                        className="form-input"
                                        placeholder="votre@email.com"
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Entreprise (optionnel)</label>
                                    <input
                                        type="text"
                                        name="company"
                                        value={formData.company}
                                        onChange={handleInputChange}
                                        disabled={!isEditing}
                                        className="form-input"
                                        placeholder="Nom de votre entreprise"
                                    />
                                </div>
                                <div className="form-group full-width">
                                    <label>Bio (optionnel)</label>
                                    <textarea
                                        name="bio"
                                        value={formData.bio}
                                        onChange={handleInputChange}
                                        disabled={!isEditing}
                                        className="form-textarea"
                                        placeholder="Parlez-nous de vous..."
                                        rows="3"
                                    />
                                </div>
                            </div>
                            
                            {isEditing && (
                                <div className="form-actions">
                                    <button 
                                        className="btn-cancel" 
                                        onClick={() => {
                                            setIsEditing(false);
                                            loadUserProfile();
                                        }}
                                        disabled={isSaving}
                                    >
                                        Annuler
                                    </button>
                                    <button 
                                        className="btn-save" 
                                        onClick={handleSaveProfile}
                                        disabled={isSaving}
                                    >
                                        {isSaving ? 'Enregistrement...' : 'Enregistrer'}
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Password Change Card */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">
                                <span className="material-icons">lock</span>
                                Sécurité
                            </h3>
                            {!isChangingPassword && (
                                <button className="btn-edit" onClick={() => setIsChangingPassword(true)}>
                                    <span className="material-icons">vpn_key</span>
                                    Changer le mot de passe
                                </button>
                            )}
                        </div>
                        
                        {passwordMessage.text && (
                            <div className={`message-box ${passwordMessage.type}`}>
                                <span className="material-icons">
                                    {passwordMessage.type === 'success' ? 'check_circle' : 'error'}
                                </span>
                                <span>{passwordMessage.text}</span>
                            </div>
                        )}
                        
                        {isChangingPassword && (
                            <div className="card-body">
                                <div className="form-grid">
                                    <div className="form-group full-width">
                                        <label>Mot de passe actuel</label>
                                        <input
                                            type="password"
                                            name="currentPassword"
                                            value={passwordData.currentPassword}
                                            onChange={handlePasswordChange}
                                            className="form-input"
                                            placeholder="••••••••"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Nouveau mot de passe</label>
                                        <input
                                            type="password"
                                            name="newPassword"
                                            value={passwordData.newPassword}
                                            onChange={handlePasswordChange}
                                            className="form-input"
                                            placeholder="••••••••"
                                        />
                                        <small>Minimum 8 caractères</small>
                                    </div>
                                    <div className="form-group">
                                        <label>Confirmer le nouveau mot de passe</label>
                                        <input
                                            type="password"
                                            name="confirmPassword"
                                            value={passwordData.confirmPassword}
                                            onChange={handlePasswordChange}
                                            className="form-input"
                                            placeholder="••••••••"
                                        />
                                    </div>
                                </div>
                                
                                <div className="form-actions">
                                    <button 
                                        className="btn-cancel" 
                                        onClick={() => {
                                            setIsChangingPassword(false);
                                            setPasswordData({
                                                currentPassword: '',
                                                newPassword: '',
                                                confirmPassword: ''
                                            });
                                            setPasswordMessage({ type: '', text: '' });
                                        }}
                                        disabled={isSaving}
                                    >
                                        Annuler
                                    </button>
                                    <button 
                                        className="btn-save" 
                                        onClick={handleChangePassword}
                                        disabled={isSaving}
                                    >
                                        {isSaving ? 'Modification...' : 'Modifier le mot de passe'}
                                    </button>
                                </div>
                            </div>
                        )}
                        
                        {!isChangingPassword && (
                            <div className="card-body">
                                <div className="security-item" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 0', borderBottom: '1px solid #f1f5f9' }}>
                                    <div>
                                        <h4 style={{ margin: '0 0 0.25rem 0', fontSize: '1rem' }}>Authentification à deux facteurs (2FA)</h4>
                                        <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b' }}>
                                            Ajoute une couche de sécurité supplémentaire en demandant un code par email lors de la connexion.
                                        </p>
                                    </div>
                                    <div className="toggle-switch">
                                        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                                            <input 
                                                type="checkbox" 
                                                checked={is2FAEnabled} 
                                                onChange={handleToggle2FA}
                                                disabled={isToggling2FA}
                                                style={{ marginRight: '0.5rem' }}
                                            />
                                            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: is2FAEnabled ? '#10b981' : '#64748b' }}>
                                                {is2FAEnabled ? 'Activé' : 'Désactivé'}
                                            </span>
                                        </label>
                                    </div>
                                </div>

                                <p className="security-info">
                                    <span className="material-icons">info</span>
                                    Dernière modification: {userStats.lastLogin || 'Jamais'}
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Account Info */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">
                                <span className="material-icons">info</span>
                                Informations du compte
                            </h3>
                        </div>
                        <div className="card-body">
                            <div className="info-grid">
                                <div className="info-item">
                                    <span className="info-label">Membre depuis</span>
                                    <span className="info-value">{userStats.memberSince || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Dernière connexion</span>
                                    <span className="info-value">{userStats.lastLogin || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">ID Utilisateur</span>
                                    <span className="info-value">#{user?.id || 'N/A'}</span>
                                </div>
                                <div className="info-item">
                                    <span className="info-label">Rôle</span>
                                    <span className="info-value">{formData.role === 'admin' ? 'Administrateur' : 'Utilisateur'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Danger Zone */}
                    <div className="card danger-zone">
                        <div className="card-header">
                            <h3 className="card-title">
                                <span className="material-icons">warning</span>
                                Zone de danger
                            </h3>
                        </div>
                        <div className="card-body">
                            <p className="danger-warning">
                                La suppression de votre compte est définitive et irréversible. 
                                Toutes vos données seront perdues.
                            </p>
                            <button className="btn-danger" onClick={handleDeleteAccount}>
                                <span className="material-icons">delete_forever</span>
                                Supprimer mon compte
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Profile;
