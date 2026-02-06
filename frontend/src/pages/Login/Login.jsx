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
  const { login, verify2FA } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    code: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [show2FA, setShow2FA] = useState(false);

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

    if (!show2FA) {
      // Étape 1 : Login normal
      if (!formData.email || !formData.password) {
        setError('Veuillez remplir tous les champs');
        return;
      }

      setIsLoading(true);
      const result = await login(formData.email, formData.password);
      setIsLoading(false);

      if (result.success) {
        if (result.requires2FA) {
          setShow2FA(true);
          setError('Code de vérification envoyé par email');
        } else {
          navigate('/dashboard');
        }
      } else {
        setError(result.error || 'Erreur de connexion');
      }
    } else {
      // Étape 2 : Vérification 2FA
      if (!formData.code) {
        setError('Veuillez entrer le code reçu par email');
        return;
      }

      setIsLoading(true);
      const result = await verify2FA(formData.email, formData.password, formData.code);
      setIsLoading(false);

      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.error || 'Code incorrect');
      }
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
            <h1>{show2FA ? 'Vérification 2FA' : 'Connexion'}</h1>
            <p className="subtitle">{show2FA ? 'Entrez le code reçu par email' : 'Accédez à votre espace de scraping'}</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠</span>
                {error}
              </div>
            )}

            {!show2FA ? (
              <>
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
                  <div style={{ textAlign: 'right', marginTop: '0.5rem' }}>
                    <Link to="/forgot-password" style={{ fontSize: '0.8rem', color: '#64748b', textDecoration: 'none' }}>
                      Mot de passe oublié ?
                    </Link>
                  </div>
                </div>
              </>
            ) : (
              <div className="form-group">
                <label htmlFor="code">
                  <span className="label-icon">🔑</span>
                  Code de vérification
                </label>
                <input
                  type="text"
                  id="code"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  placeholder="123456"
                  disabled={isLoading}
                  autoComplete="one-time-code"
                  maxLength="6"
                  style={{ letterSpacing: '0.5em', textAlign: 'center', fontSize: '1.2em' }}
                />
              </div>
            )}

            <button 
              type="submit" 
              className="login-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Vérification...
                </>
              ) : (
                <>
                  <span>{show2FA ? 'Vérifier' : 'Se connecter'}</span>
                  <span className="btn-icon">→</span>
                </>
              )}
            </button>
            
            {show2FA && (
               <button 
                type="button" 
                className="login-btn"
                onClick={() => setShow2FA(false)}
                style={{ marginTop: '10px', background: 'transparent', border: '1px solid #e2e8f0', color: '#64748b' }}
              >
                Retour
              </button>
            )}
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
