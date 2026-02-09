import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';

const Header = ({ title }) => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();

    const handleNewScraping = () => {
        navigate('/analysis');
    };

    return (
        <header className="page-header">
            <h1 className="page-title">{title}</h1>
            <div className="header-actions">
                <button className="btn-primary" onClick={handleNewScraping}>
                    <span className="material-icons">add</span>
                    Nouveau scraping
                </button>
                <div className="user-profile" onClick={() => navigate('/profile')} style={{ cursor: 'pointer' }} title="Mon profil">
                    {user?.avatar ? (
                        <div className="avatar">
                            <img
                                src={user.avatar}
                                alt="Avatar"
                                className="avatar-img"
                                style={{ width: 40, height: 40, borderRadius: '50%', objectFit: 'cover' }}
                            />
                        </div>
                    ) : (
                        <div className="avatar">{user?.name?.substring(0, 2).toUpperCase() || 'U'}</div>
                    )}
                    <div className="user-info" style={{ display: 'flex', flexDirection: 'column', marginLeft: '0.5rem' }}>
                        <span className="user-name" style={{ fontWeight: 600, fontSize: '0.9rem' }}>{user?.name || 'Utilisateur'}</span>
                        <span className="user-email" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{user?.email}</span>
                    </div>
                </div>
                <button onClick={toggleTheme} className="btn-theme-toggle">
                    <span className="material-icons">{theme === 'dark' ? 'light_mode' : 'dark_mode'}</span>
                </button>
                <button className="btn-logout" onClick={async () => { await logout(); navigate('/login'); }}>
                    <span className="material-icons">logout</span>
                    Déconnexion
                </button>
            </div>
        </header>
    );
};

export default Header;
