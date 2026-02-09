// frontend/src/pages/Register/Register.jsx
// Page d'inscription avec formulaire de création de compte
// Permet aux nouveaux utilisateurs de créer un compte et redirige vers le dashboard
// RELEVANT FILES: frontend/src/contexts/AuthContext.jsx, frontend/src/pages/Login/Login.jsx, frontend/src/assets/css/register.css, frontend/src/App.jsx

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import '../../assets/css/register.css';

  import PublicHeader from '../../components/Public/PublicHeader';

const Register = () => {
  const navigate = useNavigate();
  const { register, verifyEmail } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    code: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showVerification, setShowVerification] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error for the field being edited
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Le nom est requis';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Le nom doit contenir au moins 2 caractères';
    }

    if (!formData.email) {
      newErrors.email = 'L\'email est requis';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email invalide';
    }

    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Veuillez confirmer le mot de passe';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    if (!showVerification) {
        if (!validateForm()) {
          return;
        }

        setIsLoading(true);
        
        const result = await register(formData.name, formData.email, formData.password);
        
        setIsLoading(false);

        if (result.success) {
          if (result.verificationRequired) {
              setShowVerification(true);
          } else {
              navigate('/dashboard');
          }
        } else {
          setErrors({ submit: result.error || 'Erreur lors de l\'inscription' });
        }
    } else {
        if (!formData.code) {
            setErrors({ submit: 'Veuillez entrer le code de vérification' });
            return;
        }

        setIsLoading(true);
        const result = await verifyEmail(formData.email, formData.code);
        setIsLoading(false);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setErrors({ submit: result.error || 'Code incorrect' });
        }
    }
  };

  return (
    <div className="register-page">
      <PublicHeader />
      <div className="register-background">
        <div className="grid-overlay"></div>
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      <div className="register-container">
        <div className="register-card">
          <div className="register-header">
            <div className="icon-wrapper">
              <span className="register-icon">★</span>
            </div>
            <h1>{showVerification ? 'Vérifiez votre email' : 'Créer un compte'}</h1>
            <p className="subtitle">{showVerification ? 'Un code a été envoyé à ' + formData.email : 'Commencez à scraper en quelques secondes'}</p>
          </div>

          <form onSubmit={handleSubmit} className="register-form">
            {errors.submit && (
              <div className="error-message">
                <span className="error-icon">⚠</span>
                {errors.submit}
              </div>
            )}

            {!showVerification ? (
                <>
                <div className="form-group">
                <label htmlFor="name">
                    <span className="label-icon">👤</span>
                    Nom complet
                </label>
                <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Jean Dupont"
                    disabled={isLoading}
                    autoComplete="name"
                    className={errors.name ? 'error' : ''}
                />
                {errors.name && <span className="field-error">{errors.name}</span>}
                </div>

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
                    className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="field-error">{errors.email}</span>}
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
                    autoComplete="new-password"
                    className={errors.password ? 'error' : ''}
                />
                {errors.password && <span className="field-error">{errors.password}</span>}
                </div>

                <div className="form-group">
                <label htmlFor="confirmPassword">
                    <span className="label-icon">🔒</span>
                    Confirmer le mot de passe
                </label>
                <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="••••••••"
                    disabled={isLoading}
                    autoComplete="new-password"
                    className={errors.confirmPassword ? 'error' : ''}
                />
                {errors.confirmPassword && <span className="field-error">{errors.confirmPassword}</span>}
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
              className="register-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  {showVerification ? 'Vérification...' : 'Création du compte...'}
                </>
              ) : (
                <>
                  <span>{showVerification ? 'Vérifier' : 'Créer mon compte'}</span>
                  <span className="btn-icon">→</span>
                </>
              )}
            </button>
          </form>

          <div className="register-footer">
            <p>
              Vous avez déjà un compte ?{' '}
              <Link to="/login" className="login-link">
                Se connecter
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
