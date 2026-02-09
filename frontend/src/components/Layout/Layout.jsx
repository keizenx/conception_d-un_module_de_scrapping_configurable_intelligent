import React from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import Header from './Header';
import '../../assets/css/dashboard.css'; // On réutilise le CSS pour le moment

const Layout = ({ children, title }) => {
    const navigate = useNavigate();

    return (
        <div className="app-container">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
                    <div className="logo-icon"><span className="material-icons">flash_on</span></div>
                    SCRAPER PRO
                </div>
                <nav className="sidebar-nav">
                    <NavLink to="/dashboard" className="nav-link">
                        <span className="material-icons">dashboard</span>
                        Dashboard
                    </NavLink>
                    <NavLink to="/analysis" className="nav-link">
                        <span className="material-icons">travel_explore</span>
                        Nouvelle Analyse
                    </NavLink>
                    <NavLink to="/results" className="nav-link">
                        <span className="material-icons">poll</span>
                        Résultats
                    </NavLink>
                    <NavLink to="/reports" className="nav-link">
                        <span className="material-icons">assessment</span>
                        Rapports
                    </NavLink>
                    <NavLink to="/settings" className="nav-link">
                        <span className="material-icons">settings</span>
                        Paramètres
                    </NavLink>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <Header title={title} />
                {children}
            </main>
        </div>
    );
};

export default Layout;
