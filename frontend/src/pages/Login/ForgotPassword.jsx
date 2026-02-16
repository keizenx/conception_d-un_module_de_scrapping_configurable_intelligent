// frontend/src/pages/Login/ForgotPassword.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import '../../assets/css/login.css';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email) {
      setError('Veuillez entrer votre email');
      return;
    }

    setIsLoading(true);
    try {
      await api.forgotPassword(email);
      setSuccess('Si cet email existe, un code de réinitialisation vous a été envoyé.');
      // Rediriger vers la page de réinitialisation après 3 secondes ou immédiatement avec l'email en state
      setTimeout(() => {
        navigate('/reset-password', { state: { email } });
      }, 2000);
    } catch (err) {
      setError(err.message || 'Une erreur est survenue');
    } finally {
      setIsLoading(false);
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
              <span className="login-icon">🔄</span>
            </div>
            <h1>Mot de passe oublié</h1>
            <p className="subtitle">Entrez votre email pour recevoir un code</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠</span>
                {error}
              </div>
            )}
            
            {success && (
              <div className="success-message" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1.5rem', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                <span className="success-icon">✓</span>
                {success}
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
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="votre@email.com"
                disabled={isLoading}
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
                  Envoi...
                </>
              ) : (
                <>
                  <span>Envoyer le code</span>
                  <span className="material-icons btn-icon">arrow_forward</span>
                </>
              )}
            </button>
            
            <Link to="/login" className="login-btn" style={{ marginTop: '10px', background: 'transparent', border: '1px solid #e2e8f0', color: '#64748b', textDecoration: 'none', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                Retour à la connexion
            </Link>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
