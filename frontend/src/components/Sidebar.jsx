import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="sidebar">
      <div className="logo">
        <h1>Scraper Pro</h1>
        <span className="version">Enterprise v2.4.0</span>
      </div>

      <nav className="main-nav">
        <Link to="/dashboard" className={`nav-item ${location.pathname === '/dashboard' ? 'active' : ''}`}>
          <i className="fas fa-chart-bar"></i>
          <span>Tableau de Bord</span>
        </Link>
        {/* <Link to="/results" className={`nav-item ${location.pathname === '/results' ? 'active' : ''}`}>
          <i className="fas fa-tasks"></i>
          <span>Rapports</span>
        </Link> */}
        <Link to="/analysis" className={`nav-item ${location.pathname === '/analysis' ? 'active' : ''}`}>
          <i className="fas fa-chart-line"></i>
          <span>Analyse</span>
        </Link>
        <Link to="/results" className={`nav-item ${location.pathname === '/results' ? 'active' : ''}`}>
          <i className="fas fa-database"></i>
          <span>Résultats</span>
        </Link>
      </nav>

      <div className="user-info">
        <div className="user-avatar">
          <i className="fas fa-user-circle"></i>
        </div>
        <div className="user-details">
          <span className="user-name">Jean Dupont</span>
          <span className="user-role">Utilisateur</span>
        </div>
        <Link to="/login" className="logout-btn">
          <i className="fas fa-sign-out-alt"></i>
        </Link>
      </div>
    </aside>
  );
};

export default Sidebar;