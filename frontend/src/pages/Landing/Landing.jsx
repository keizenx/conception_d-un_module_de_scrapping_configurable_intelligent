// frontend/src/pages/Landing/Landing.jsx
// Page d'accueil de Scraper Pro avec présentation des fonctionnalités
// Cette page sert de vitrine pour attirer les utilisateurs et expliquer le produit
// RELEVANT FILES: frontend/src/App.jsx, frontend/src/assets/css/landing.css, frontend/src/pages/Login/Login.jsx, frontend/src/pages/Register/Register.jsx

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import '../../assets/css/landing.css';

const Landing = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [quickUrl, setQuickUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  
  // Rediriger vers dashboard si déjà connecté (désactivé temporairement)
  // useEffect(() => {
  //   if (user) {
  //     navigate('/dashboard');
  //   }
  // }, [user, navigate]);
  
  useEffect(() => {
    // Smooth scroll for navigation
    const handleAnchorClick = (e) => {
      const href = e.target.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    };

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', handleAnchorClick);
    });

    // Feature cards animation on scroll
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, index * 100);
        }
      });
    }, observerOptions);

    document.querySelectorAll('.feature-card').forEach((card, index) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(30px)';
      card.style.transition = `all 0.6s ease ${index * 0.1}s`;
      observer.observe(card);
    });

    return () => {
      document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.removeEventListener('click', handleAnchorClick);
      });
    };
  }, []);
  
  // Quick analyze function
  const handleQuickAnalyze = async () => {
    if (!quickUrl.trim()) {
      alert('Veuillez entrer une URL');
      return;
    }
    
    // Normaliser l'URL
    let normalizedUrl = quickUrl.trim();
    if (!normalizedUrl.startsWith('http://') && !normalizedUrl.startsWith('https://')) {
      normalizedUrl = `https://${normalizedUrl}`;
    }
    
    setIsAnalyzing(true);
    setShowLoginPrompt(false);
    
    try {
      // Analyse rapide sans authentification
      const result = await api.quickAnalyze(normalizedUrl);
      setAnalysisResult(result);
      
      // Afficher le prompt de connexion après l'analyse
      setShowLoginPrompt(true);
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
      alert('Erreur lors de l\'analyse du site. Veuillez réessayer.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="landing-page">
      {/* Navigation */}
      <nav>
        <div className="logo">
          <div className="logo-icon"><span className="material-icons">flash_on</span></div>
          SCRAPER PRO
        </div>
        <ul>
          <li><a href="#services">Services</a></li>
          <li><a href="#features">Fonctionnalités</a></li>
          <li><a href="#tech">Technologies</a></li>
          <li><a href="#equipe">Équipe</a></li>
          <li><a href="#contact">Contact</a></li>
        </ul>
        <Link to="/login" className="cta-button">DÉMARRER</Link>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span>⚡</span>
            <span>Propulsé par Django & React</span>
          </div>
          <h1>
            Automatisez <span className="highlight">tout</span><br />
            sur le web
          </h1>
          <p>
            Scraper Pro automatise vos processus web, pour que vous puissiez vous concentrer sur l'essentiel.
          </p>
          
          {/* Quick Scraper */}
          <div className="quick-scraper">
            <div className="quick-scraper-input">
              <input
                type="text"
                placeholder="https://example.com"
                value={quickUrl}
                onChange={(e) => setQuickUrl(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleQuickAnalyze()}
                disabled={isAnalyzing}
              />
              <button 
                onClick={handleQuickAnalyze}
                disabled={isAnalyzing}
                className="btn-analyze"
              >
                {isAnalyzing ? '⏳ Analyse...' : '🚀 Analyser'}
              </button>
            </div>
            
            {/* Analysis Results Preview */}
            {analysisResult && (
              <div className="quick-results">
                <div className="result-stats">
                  <div className="stat-item">
                    <span className="stat-icon">📄</span>
                    <span className="stat-label">{analysisResult.page_count || 0} pages</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">🌐</span>
                    <span className="stat-label">{analysisResult.subdomains?.total_found || 0} sous-domaines</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">📦</span>
                    <span className="stat-label">{analysisResult.content_types_count || 0} types de contenu</span>
                  </div>
                </div>
                
                {showLoginPrompt && (
                  <div className="login-prompt">
                    <div className="prompt-content">
                      <span className="prompt-icon">🔒</span>
                      <p>Connectez-vous pour accéder à l'analyse complète et lancer le scraping</p>
                      <div className="prompt-buttons">
                        <Link to="/login" className="btn-prompt-login">Se connecter</Link>
                        <Link to="/register" className="btn-prompt-register">Créer un compte</Link>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

      </section>

      {/* Features Intro */}
      <section className="features-intro" id="features">
        <h2>Tout ce que vous faites dans votre navigateur,<br />nous le codons pour vous</h2>
        <p>
          Gagnez du temps avec l'automatisation. Voici quelques tâches courantes que nous automatisons quotidiennement :
        </p>
      </section>

      {/* Features Grid */}
      <section className="features-grid" id="services">

        <div className="feature-card">
          <div className="feature-icon">🧭</div>
          <h3>Navigation</h3>
          <p>Parcours intelligent des pages</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🔄</div>
          <h3>Actions multi-pages</h3>
          <p>Workflows complexes simplifiés</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>Extraction de données</h3>
          <p>Collecte structurée et précise</p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🤖</div>
          <h3>Automatisation intelligente</h3>
          <p>Scripts adaptatifs et évolutifs</p>
        </div>
      </section>

      {/* Communication Section */}
      <section className="communication" id="tech">
        <div className="communication-container">
          <div className="comm-visual">
            <div className="code-window">
              <div className="window-header">
                <div className="window-dot dot-red"></div>
                <div className="window-dot dot-yellow"></div>
                <div className="window-dot dot-green"></div>
              </div>
              <div className="code-content">
                <code className="code-line"><span className="code-comment"># API REST avec Django</span></code>
                <code className="code-line"><span className="code-keyword">from</span> rest_framework <span className="code-keyword">import</span> viewsets</code>
                <code className="code-line"><span className="code-keyword">from</span> rest_framework.decorators <span className="code-keyword">import</span> action</code>
                <code className="code-line"><span className="code-keyword">from</span> playwright.sync_api <span className="code-keyword">import</span> sync_playwright</code>
                <code className="code-line"></code>
                <code className="code-line"><span className="code-keyword">class</span> <span className="code-function">ScrapingViewSet</span>(viewsets.ViewSet):</code>
                <code className="code-line">    <span className="code-keyword">@action</span>(detail=<span className="code-keyword">False</span>, methods=[<span className="code-string">'post'</span>])</code>
                <code className="code-line">    <span className="code-keyword">def</span> <span className="code-function">analyze</span>(self, request):</code>
                <code className="code-line">        url = request.data.<span className="code-function">get</span>(<span className="code-string">'url'</span>)</code>
                <code className="code-line">        <span className="code-keyword">with</span> <span className="code-function">sync_playwright</span>() <span className="code-keyword">as</span> p:</code>
                <code className="code-line">            browser = p.chromium.<span className="code-function">launch</span>()</code>
                <code className="code-line">            page = browser.<span className="code-function">new_page</span>()</code>
                <code className="code-line">            page.<span className="code-function">goto</span>(url)</code>
                <code className="code-line">            data = page.<span className="code-function">evaluate</span>(<span className="code-string">'() =&gt; {'{...}'}'</span>)</code>
                <code className="code-line">            <span className="code-keyword">return</span> Response({'{'}<span className="code-string">'data'</span>: data{'}'})</code>
              </div>
            </div>
          </div>

          <div className="comm-content">
            <h2>Architecture hors navigateur</h2>
            <p>
              Notre stack technologique moderne combine la puissance de React.js pour une interface utilisateur fluide avec Django REST Framework et Playwright pour un scraping robuste côté serveur.
            </p>
            <p>
              L'architecture séparée front/back garantit des performances optimales et une scalabilité sans limites.
            </p>

            <div className="tech-stack">
              <div className="tech-badge">React.js</div>
              <div className="tech-badge">Django</div>
              <div className="tech-badge">Playwright</div>
              <div className="tech-badge">SQLite</div>
              <div className="tech-badge">Tailwind CSS</div>
              <div className="tech-badge">Chart.js</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="equipe">
        <div className="footer-content">
          <div className="footer-logo">⚡ SCRAPER PRO</div>
          <p className="footer-text">
            Solution d'automatisation web professionnelle
          </p>

          <div className="team-info">
            <p><strong>Équipe de développement :</strong></p>
            <p>
              Koffi Ornella (Front-end) • Oumar Vivien (Back-end) •
              Kouakou Jean Raphael (Back-end) • Kouame Aka Richard (Product Owner) •
              Beleley Franck (Scrum Master)
            </p>
            <p style={{ marginTop: '1.5rem', color: 'var(--text-muted)' }}>
              Sprint 2026
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
