// frontend/src/pages/Login/Login.jsx
// Page de connexion avec formulaire d'authentification
// Permet aux utilisateurs de se connecter et redirige vers le dashboard
// RELEVANT FILES: frontend/src/contexts/AuthContext.jsx, frontend/src/pages/Register/Register.jsx, frontend/src/assets/css/login.css, frontend/src/App.jsx

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import '../../assets/css/login.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.email || !formData.password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    setIsLoading(true);
    
    const result = await login(formData.email, formData.password);
    
    setIsLoading(false);

    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error || 'Erreur de connexion');
    }
  };

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="grid-overlay"></div>
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      <nav className="login-nav">
        <Link to="/" className="logo">
          <span className="logo-icon">◆</span>
          <span>SCRAPER PRO</span>
        </Link>
      </nav>

      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <div className="icon-wrapper">
              <span className="login-icon">⚡</span>
            </div>
            <h1>Connexion</h1>
            <p className="subtitle">Accédez à votre espace de scraping</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠</span>
                {error}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">
                <span className="label-icon">✉</span>
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="votre@email.com"
                disabled={isLoading}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">
                <span className="label-icon">🔒</span>
                Mot de passe
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>

            <button 
              type="submit" 
              className="login-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Connexion en cours...
                </>
              ) : (
                <>
                  <span>Se connecter</span>
                  <span className="btn-icon">→</span>
                </>
              )}
            </button>
          </form>

          <div className="login-footer">
            <p>
              Pas encore de compte ?{' '}
              <Link to="/register" className="register-link">
                S'inscrire gratuitement
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
