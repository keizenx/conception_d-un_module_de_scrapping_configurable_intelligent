import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { Link, useLocation } from 'react-router-dom';
import '../../assets/css/public-header.css';

const PublicHeader = () => {
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();

    return (
        <header className="public-header">
            <div className="logo">
                <Link to="/">
                    <span className="logo-text">SCRAPER PRO</span>
                </Link>
            </div>
            <div className="header-actions">
                <nav className="public-nav">
                    {location.pathname === '/' && (
                        <>
                            <Link to="/login" className="nav-link">Login</Link>
                            <Link to="/register" className="nav-link btn-register">Register</Link>
                        </>
                    )}
                    {location.pathname === '/register' && (
                        <Link to="/login" className="nav-link">Login</Link>
                    )}
                </nav>
                <button onClick={toggleTheme} className="btn-theme-toggle">
                    <span className="material-icons">{theme === 'dark' ? 'light_mode' : 'dark_mode'}</span>
                </button>
            </div>
        </header>
    );
};

export default PublicHeader;
