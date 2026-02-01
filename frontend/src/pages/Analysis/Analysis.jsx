// src/pages/Analysis/Analysis.jsx - VERSION COMPLÈTE
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import Sidebar from '../../components/Sidebar';
import '../../assets/css/dashboard.css';
import '../../assets/css/analysis.css';

const Analysis = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const searchParams = new URLSearchParams(location.search);
  const inputParam = searchParams.get('input') || '';
  const typeParam = searchParams.get('type') || 'url';

  const [analysis, setAnalysis] = useState({
    isLoading: false,
    isComplete: false,
    progress: 0,
    error: null
  });

  const [targetInfo, setTargetInfo] = useState({
    input: inputParam,
    type: typeParam,
    title: '',
    favicon: '',
    lastAnalyzed: '',
    totalElements: 0,
    successRate: 0
  });

  const [detectedElements, setDetectedElements] = useState([]);
  const [scrapingConfig, setScrapingConfig] = useState({
    name: '',
    schedule: 'manual',
    depth: 1,
    pagination: true,
    saveFormat: 'json',
    maxPages: 10
  });

  // Détecter le type d'entrée
  const detectInputType = (input) => {
    const trimmed = input.trim();
    
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      return 'url';
    }
    
    if (trimmed.includes('<') && trimmed.includes('>')) {
      return 'html';
    }
    
    return 'selector';
  };

  // Détecter le type de site depuis l'URL
  const detectSiteTypeFromUrl = (url) => {
    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname.toLowerCase();
      
      // E-commerce
      if (hostname.includes('amazon') || hostname.includes('ebay') || 
          hostname.includes('aliexpress') || hostname.includes('shop') ||
          hostname.includes('darty') || hostname.includes('fnac') ||
          hostname.includes('cdiscount') || hostname.includes('boulanger')) {
        return 'ecommerce';
      }
      
      // Templates
      if (hostname.includes('template') || hostname.includes('theme') ||
          hostname.includes('themeforest') || hostname.includes('creativemarket')) {
        return 'template';
      }
      
      // Blogs
      if (hostname.includes('blog') || hostname.includes('medium') || 
          hostname.includes('wordpress') || hostname.includes('blogger') ||
          hostname.includes('tumblr') || hostname.includes('dev.to')) {
        return 'blog';
      }
      
      // GitHub
      if (hostname.includes('github')) {
        return 'github';
      }
      
      // Actualités
      if (hostname.includes('news') || hostname.includes('lemonde') ||
          hostname.includes('figaro') || hostname.includes('20minutes')) {
        return 'news';
      }
      
      return 'generic';
    } catch {
      return 'generic';
    }
  };

  // Détecter le type de contenu depuis le sélecteur CSS
  const detectContentTypeFromSelector = (selector) => {
    const sel = selector.toLowerCase();
    
    if (sel.includes('.product') || sel.includes('.item') || sel.includes('.card')) {
      return 'ecommerce';
    } else if (sel.includes('.template') || sel.includes('.theme')) {
      return 'template';
    } else if (sel.includes('article') || sel.includes('.post') || sel.includes('.blog')) {
      return 'blog';
    } else if (sel.includes('.repo') || sel.includes('.repository')) {
      return 'github';
    } else if (sel.includes('.news') || sel.includes('.article')) {
      return 'news';
    } else if (sel.includes('#price') || sel.includes('.price')) {
      return 'price';
    } else if (sel.includes('.image') || sel.includes('img')) {
      return 'image';
    } else if (sel.includes('h1') || sel.includes('h2') || sel.includes('.title')) {
      return 'title';
    }
    
    return 'generic';
  };

  // Générer des données mock selon le type de contenu
  const generateMockElements = (input, inputType) => {
    // Si c'est un sélecteur CSS
    if (inputType === 'selector') {
      const contentType = detectContentTypeFromSelector(input);
      
      switch(contentType) {
        case 'ecommerce':
          return [
            { id: 1, name: 'Produits', icon: 'fas fa-box', count: 45, selector: input, confidence: 95, isSelected: true },
            { id: 2, name: 'Prix', icon: 'fas fa-tag', count: 45, selector: input + ' .price', confidence: 92, isSelected: true },
            { id: 3, name: 'Images', icon: 'fas fa-image', count: 45, selector: input + ' img', confidence: 90, isSelected: true },
            { id: 4, name: 'Titres', icon: 'fas fa-heading', count: 45, selector: input + ' h3', confidence: 88, isSelected: true },
            { id: 5, name: 'Liens', icon: 'fas fa-link', count: 45, selector: input + ' a', confidence: 85, isSelected: false }
          ];
        
        case 'template':
          return [
            { id: 1, name: 'Templates', icon: 'fas fa-palette', count: 32, selector: input, confidence: 96, isSelected: true },
            { id: 2, name: 'Prix', icon: 'fas fa-tag', count: 32, selector: input + ' .price', confidence: 94, isSelected: true },
            { id: 3, name: 'Démos', icon: 'fas fa-eye', count: 32, selector: input + ' .demo-link', confidence: 92, isSelected: true },
            { id: 4, name: 'Catégories', icon: 'fas fa-tags', count: 8, selector: input + ' .category', confidence: 89, isSelected: true },
            { id: 5, name: 'Avis', icon: 'fas fa-star', count: 128, selector: input + ' .review', confidence: 86, isSelected: false }
          ];
        
        case 'blog':
          return [
            { id: 1, name: 'Articles', icon: 'fas fa-newspaper', count: 25, selector: input, confidence: 97, isSelected: true },
            { id: 2, name: 'Titres', icon: 'fas fa-heading', count: 25, selector: input + ' h2', confidence: 95, isSelected: true },
            { id: 3, name: 'Dates', icon: 'fas fa-calendar', count: 25, selector: input + ' .date', confidence: 93, isSelected: true },
            { id: 4, name: 'Auteurs', icon: 'fas fa-user', count: 8, selector: input + ' .author', confidence: 90, isSelected: true },
            { id: 5, name: 'Commentaires', icon: 'fas fa-comment', count: 150, selector: input + ' .comment', confidence: 87, isSelected: false }
          ];
        
        case 'price':
          return [
            { id: 1, name: 'Prix', icon: 'fas fa-tag', count: 67, selector: input, confidence: 98, isSelected: true },
            { id: 2, name: 'Devises', icon: 'fas fa-euro-sign', count: 67, selector: input, confidence: 96, isSelected: true },
            { id: 3, name: 'Produits associés', icon: 'fas fa-box', count: 67, selector: input.replace('#price', '.product'), confidence: 85, isSelected: false },
            { id: 4, name: 'Promotions', icon: 'fas fa-percentage', count: 12, selector: input + '.sale', confidence: 82, isSelected: false }
          ];
        
        default:
          return [
            { id: 1, name: 'Éléments ciblés', icon: 'fas fa-bullseye', count: 45, selector: input, confidence: 95, isSelected: true },
            { id: 2, name: 'Contenu texte', icon: 'fas fa-font', count: 45, selector: input, confidence: 92, isSelected: true },
            { id: 3, name: 'Attributs', icon: 'fas fa-code', count: 135, selector: input, confidence: 88, isSelected: false },
            { id: 4, name: 'Éléments enfants', icon: 'fas fa-sitemap', count: 89, selector: input + ' *', confidence: 85, isSelected: false }
          ];
      }
    }
    
    // Si c'est du HTML
    if (inputType === 'html') {
      return [
        { id: 1, name: 'Balises HTML', icon: 'fas fa-code', count: countHtmlTags(input), selector: 'balises', confidence: 94, isSelected: true },
        { id: 2, name: 'Contenu texte', icon: 'fas fa-font', count: countTextNodes(input), selector: 'texte', confidence: 92, isSelected: true },
        { id: 3, name: 'Attributs', icon: 'fas fa-tag', count: countAttributes(input), selector: 'attributs', confidence: 89, isSelected: true },
        { id: 4, name: 'Liens', icon: 'fas fa-link', count: countLinks(input), selector: 'a', confidence: 87, isSelected: false },
        { id: 5, name: 'Images', icon: 'fas fa-image', count: countImages(input), selector: 'img', confidence: 85, isSelected: false }
      ];
    }
    
    // Si c'est une URL
    const siteType = detectSiteTypeFromUrl(input);
    
    switch(siteType) {
      case 'ecommerce':
        return [
          { id: 1, name: 'Produits', icon: 'fas fa-box', count: 142, selector: '.product-card, .item', confidence: 98, isSelected: true },
          { id: 2, name: 'Prix', icon: 'fas fa-tag', count: 142, selector: '.price, .amount', confidence: 96, isSelected: true },
          { id: 3, name: 'Images', icon: 'fas fa-image', count: 245, selector: 'img.product-image, .product-img', confidence: 95, isSelected: true },
          { id: 4, name: 'Descriptions', icon: 'fas fa-align-left', count: 142, selector: '.product-description, .description', confidence: 92, isSelected: true },
          { id: 5, name: 'Avis', icon: 'fas fa-star', count: 428, selector: '.review-item, .rating', confidence: 88, isSelected: false },
          { id: 6, name: 'Catégories', icon: 'fas fa-tags', count: 12, selector: '.category-link, .breadcrumb', confidence: 90, isSelected: true }
        ];
      
      case 'template':
        return [
          { id: 1, name: 'Templates', icon: 'fas fa-palette', count: 56, selector: '.template-card, .theme-item', confidence: 97, isSelected: true },
          { id: 2, name: 'Prix', icon: 'fas fa-tag', count: 56, selector: '.template-price, .price-tag', confidence: 96, isSelected: true },
          { id: 3, name: 'Catégories', icon: 'fas fa-tags', count: 8, selector: '.category-item, .filter-category', confidence: 94, isSelected: true },
          { id: 4, name: 'Démos', icon: 'fas fa-eye', count: 56, selector: '.demo-link, .preview-button', confidence: 97, isSelected: false },
          { id: 5, name: 'Images', icon: 'fas fa-image', count: 168, selector: 'img.template-preview, .screenshot', confidence: 95, isSelected: true },
          { id: 6, name: 'Descriptions', icon: 'fas fa-align-left', count: 56, selector: '.template-description, .features', confidence: 92, isSelected: true }
        ];
      
      case 'blog':
        return [
          { id: 1, name: 'Articles', icon: 'fas fa-newspaper', count: 45, selector: 'article, .post', confidence: 97, isSelected: true },
          { id: 2, name: 'Titres', icon: 'fas fa-heading', count: 45, selector: 'h1.article-title, .post-title', confidence: 98, isSelected: true },
          { id: 3, name: 'Auteurs', icon: 'fas fa-user', count: 12, selector: '.author-name, .post-author', confidence: 92, isSelected: true },
          { id: 4, name: 'Dates', icon: 'fas fa-calendar', count: 45, selector: '.date-published, .post-date', confidence: 94, isSelected: true },
          { id: 5, name: 'Catégories', icon: 'fas fa-tags', count: 8, selector: '.category-tag, .post-category', confidence: 90, isSelected: false },
          { id: 6, name: 'Commentaires', icon: 'fas fa-comment', count: 236, selector: '.comment, .comment-item', confidence: 88, isSelected: false }
        ];
      
      case 'github':
        return [
          { id: 1, name: 'Répositories', icon: 'fas fa-code-branch', count: 25, selector: '.repo-item, .repository', confidence: 96, isSelected: true },
          { id: 2, name: 'Stars', icon: 'fas fa-star', count: 25, selector: '.star-count, .stars', confidence: 94, isSelected: true },
          { id: 3, name: 'Forks', icon: 'fas fa-code-fork', count: 25, selector: '.fork-count, .forks', confidence: 93, isSelected: true },
          { id: 4, name: 'Issues', icon: 'fas fa-exclamation-circle', count: 89, selector: '.issue-item, .issue', confidence: 91, isSelected: false },
          { id: 5, name: 'Langages', icon: 'fas fa-code', count: 25, selector: '.language-tag, .lang', confidence: 90, isSelected: true },
          { id: 6, name: 'Descriptions', icon: 'fas fa-align-left', count: 25, selector: '.repo-description, .description', confidence: 89, isSelected: true }
        ];
      
      default:
        return [
          { id: 1, name: 'Liens', icon: 'fas fa-link', count: 234, selector: 'a', confidence: 98, isSelected: true },
          { id: 2, name: 'Images', icon: 'fas fa-image', count: 89, selector: 'img', confidence: 96, isSelected: true },
          { id: 3, name: 'Titres', icon: 'fas fa-heading', count: 45, selector: 'h1, h2, h3', confidence: 94, isSelected: true },
          { id: 4, name: 'Listes', icon: 'fas fa-list', count: 67, selector: 'ul, ol', confidence: 91, isSelected: false },
          { id: 5, name: 'Tableaux', icon: 'fas fa-table', count: 12, selector: 'table', confidence: 89, isSelected: false },
          { id: 6, name: 'Formulaires', icon: 'fas fa-edit', count: 8, selector: 'form', confidence: 85, isSelected: false }
        ];
    }
  };

  // Fonctions utilitaires pour HTML
  const countHtmlTags = (html) => {
    return (html.match(/<[^>]+>/g) || []).length;
  };

  const countTextNodes = (html) => {
    const text = html.replace(/<[^>]+>/g, '').trim();
    return text.split(/\s+/).filter(word => word.length > 0).length;
  };

  const countAttributes = (html) => {
    return (html.match(/\w+="[^"]*"/g) || []).length;
  };

  const countLinks = (html) => {
    return (html.match(/<a\s[^>]*>/gi) || []).length;
  };

  const countImages = (html) => {
    return (html.match(/<img\s[^>]*>/gi) || []).length;
  };

  // Démarrer l'analyse (simulation)
  const startAnalysis = () => {
    if (!targetInfo.input.trim()) {
      alert('Veuillez entrer une URL, un sélecteur CSS ou du HTML à analyser');
      return;
    }

    setAnalysis({
      isLoading: true,
      isComplete: false,
      progress: 0,
      error: null
    });

    // Détecter le type d'entrée réel
    const actualInputType = detectInputType(targetInfo.input);
    
    // Simulation de progression
    const interval = setInterval(() => {
      setAnalysis(prev => {
        const newProgress = prev.progress + 20;
        
        if (newProgress >= 100) {
          clearInterval(interval);
          
          // Générer éléments selon le type
          const elements = generateMockElements(targetInfo.input, actualInputType);
          const totalElements = elements.reduce((sum, el) => sum + el.count, 0);
          const avgConfidence = Math.round(elements.reduce((sum, el) => sum + el.confidence, 0) / elements.length);
          
          // Déterminer le titre
          let title = '';
          let typeLabel = '';
          
          if (actualInputType === 'selector') {
            const contentType = detectContentTypeFromSelector(targetInfo.input);
            title = `Sélecteur CSS (${contentType === 'ecommerce' ? 'E-commerce' : 
                      contentType === 'template' ? 'Templates' :
                      contentType === 'blog' ? 'Blog' :
                      contentType === 'github' ? 'GitHub' :
                      contentType === 'price' ? 'Prix' :
                      contentType === 'image' ? 'Images' :
                      contentType === 'title' ? 'Titres' : 'Générique'})`;
            typeLabel = 'Sélecteur CSS';
          } else if (actualInputType === 'html') {
            title = 'HTML brut analysé';
            typeLabel = 'HTML';
          } else {
            const siteType = detectSiteTypeFromUrl(targetInfo.input);
            title = `${siteType === 'ecommerce' ? 'Site E-commerce' : 
                     siteType === 'template' ? 'Site de Templates' :
                     siteType === 'blog' ? 'Blog' :
                     siteType === 'github' ? 'GitHub' :
                     siteType === 'news' ? 'Site d\'Actualités' : 'Site Web'}`;
            typeLabel = 'URL';
          }
          
          setTargetInfo(prev => ({
            ...prev,
            type: actualInputType,
            title: title,
            typeLabel: typeLabel,
            lastAnalyzed: 'À l\'instant',
            totalElements: totalElements,
            successRate: avgConfidence
          }));
          
          setDetectedElements(elements);
          
          // Générer nom de projet
          if (actualInputType === 'selector') {
            const selectorName = targetInfo.input.length > 20 
              ? targetInfo.input.substring(0, 20) + '...' 
              : targetInfo.input;
            setScrapingConfig(prev => ({ ...prev, name: `Scraping: ${selectorName}` }));
          } else if (actualInputType === 'html') {
            setScrapingConfig(prev => ({ ...prev, name: 'Scraping HTML' }));
          } else {
            try {
              const urlName = new URL(targetInfo.input).hostname.replace('www.', '');
              setScrapingConfig(prev => ({ ...prev, name: `Scraping ${urlName}` }));
            } catch {
              setScrapingConfig(prev => ({ ...prev, name: `Scraping ${actualInputType}` }));
            }
          }
          
          return {
            isLoading: false,
            isComplete: true,
            progress: 100,
            error: null
          };
        }
        
        return { ...prev, progress: newProgress };
      });
    }, 400);
  };

  // Les autres fonctions restent similaires
  const toggleElementSelection = (id) => {
    setDetectedElements(prev => 
      prev.map(element => 
        element.id === id 
          ? { ...element, isSelected: !element.isSelected }
          : element
      )
    );
  };

  const toggleAllElements = (selected) => {
    setDetectedElements(prev => 
      prev.map(element => ({ ...element, isSelected: selected }))
    );
  };

//   const startScraping = () => {
//     const selectedElements = detectedElements.filter(el => el.isSelected);
    
//     if (selectedElements.length === 0) {
//       alert('Veuillez sélectionner au moins un élément à scraper');
//       return;
//     }

//     if (!scrapingConfig.name.trim()) {
//       alert('Veuillez donner un nom à votre projet de scraping');
//       return;
//     }

//     console.log('Simulation scraping:', {
//       input: targetInfo.input,
//       type: targetInfo.type,
//       selectedElements,
//       config: scrapingConfig
//     });

//     alert(`Scraping "${scrapingConfig.name}" démarré !\n\nType: ${targetInfo.typeLabel}\nÉléments: ${selectedElements.length}`);
    
//     setTimeout(() => {
//       navigate('/results');
//     }, 1500);
//   };

// Dans Analysis.jsx - MODIFIEZ LA FONCTION startScraping()

const startScraping = () => {
  const selectedElements = detectedElements.filter(el => el.isSelected);
  
  if (selectedElements.length === 0) {
    alert('Veuillez sélectionner au moins un élément à scraper');
    return;
  }

  if (!scrapingConfig.name.trim()) {
    alert('Veuillez donner un nom à votre projet de scraping');
    return;
  }

  // CRÉER LA CONFIGURATION COMPLÈTE
  const scrapingConfigComplete = {
    target: targetInfo,
    selectedElements: selectedElements, // SEULEMENT les éléments sélectionnés
    config: scrapingConfig,
    detectedElements: detectedElements, // Tous les éléments détectés
    timestamp: new Date().toISOString()
  };

  console.log('Simulation scraping:', scrapingConfigComplete);

  // SAUVEGARDER DANS localStorage AVANT LA REDIRECTION
  localStorage.setItem('scrapingConfig', JSON.stringify(scrapingConfigComplete));
  
  alert(`Scraping "${scrapingConfig.name}" démarré !\n\nType: ${targetInfo.typeLabel}\nÉléments: ${selectedElements.length}`);
  
  // Rediriger avec les données en state AUSSI
  navigate('/results', { 
    state: { scrapingData: scrapingConfigComplete } 
  });
};



  const exportConfig = () => {
    const config = {
      target: targetInfo,
      selectedElements: detectedElements.filter(el => el.isSelected),
      config: scrapingConfig,
      timestamp: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scraping-config-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Démarrer auto si input fourni
  useEffect(() => {
    if (inputParam && !analysis.isComplete && !analysis.isLoading) {
      startAnalysis();
    }
  }, [inputParam]);

  // Calcul statistiques
  const selectedCount = detectedElements.filter(el => el.isSelected).length;
  const estimatedData = detectedElements
    .filter(el => el.isSelected)
    .reduce((sum, el) => sum + el.count, 0);
  const averageConfidence = selectedCount > 0 
    ? Math.round(detectedElements
        .filter(el => el.isSelected)
        .reduce((sum, el) => sum + el.confidence, 0) / selectedCount)
    : 0;

  return (
    <div className="dashboard-container">
      <Sidebar />
      
      <main className="main-content">
        <header className="top-bar">
          <div className="breadcrumb">
            <Link to="/dashboard">Tableau de Bord</Link> / <span>Configuration du Scraping</span>
          </div>
          <div className="top-bar-actions">
            <button className="btn btn-secondary">
              <i className="fas fa-bell"></i>
              <span className="notification-count">2</span>
            </button>
          </div>
        </header>

        {/* En-tête */}
        <section className="card highlight-card">
          <div className="card-header">
            <div>
              <h3><i className="fas fa-search"></i> Analyse des Éléments Scrappables</h3>
              <p className="card-subtitle">
                {targetInfo.title || 'Analyse en attente...'}
                {targetInfo.typeLabel && <span className="type-badge">{targetInfo.typeLabel}</span>}
              </p>
            </div>
            
            {!analysis.isComplete ? (
              <button 
                className="btn btn-primary"
                onClick={startAnalysis}
                disabled={analysis.isLoading}
              >
                {analysis.isLoading ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i>
                    Analyse ({analysis.progress}%)
                  </>
                ) : (
                  <>
                    <i className="fas fa-play"></i>
                    {targetInfo.type === 'selector' ? 'Analyser le sélecteur' : 
                     targetInfo.type === 'html' ? 'Analyser le HTML' : 
                     'Analyser le site'}
                  </>
                )}
              </button>
            ) : (
              <div className="analysis-status success">
                <i className="fas fa-check-circle"></i>
                {detectedElements.length} éléments détectés
              </div>
            )}
          </div>

          <div className="target-info">
          
            {/* // src/pages/Analysis/Analysis.jsx - PARTIE MODIFIÉE */}

{/* Dans la section target-info, remplacez la partie conditionnelle par : */}
<div className="target-input">
  <i className={`fas ${
    targetInfo.type === 'url' ? 'fa-link' :
    targetInfo.type === 'selector' ? 'fa-code' :
    'fa-file-code'
  }`}></i>
  <div className="input-container">
    <strong className="input-label">
      {targetInfo.type === 'url' ? 'URL cible :' :
       targetInfo.type === 'selector' ? 'Sélecteur CSS :' :
       'HTML brut :'}
    </strong>
    
    {targetInfo.type === 'html' ? (
      <div className="html-input-wrapper">
        <textarea 
          value={targetInfo.input}
          onChange={(e) => setTargetInfo(prev => ({ ...prev, input: e.target.value }))}
          placeholder={`<div class="example">
  <h1>Titre de la page</h1>
  <p>Contenu intéressant à scraper...</p>
  <ul>
    <li>Élément 1</li>
    <li>Élément 2</li>
  </ul>
</div>`}
          className="html-textarea"
          rows="6"
          spellCheck="false"
        />
        <div className="html-input-info">
          <span className="html-stats">
            <i className="fas fa-code"></i>
            {countHtmlTags(targetInfo.input)} balises
          </span>
          <span className="html-stats">
            <i className="fas fa-font"></i>
            {countTextNodes(targetInfo.input)} mots
          </span>
          <button 
            className="btn btn-small btn-secondary"
            onClick={() => {
              // Exemple HTML prérempli
              setTargetInfo(prev => ({ 
                ...prev, 
                input: `<div class="product-card">
  <img src="product.jpg" alt="Produit" class="product-image">
  <h3 class="product-title">iPhone 15 Pro Max</h3>
  <div class="product-price">
    <span class="price">1,299€</span>
    <span class="old-price">1,499€</span>
  </div>
  <p class="product-description">Smartphone haut de gamme avec caméra avancée</p>
  <div class="product-rating">
    <span class="stars">⭐⭐⭐⭐⭐</span>
    <span class="review-count">(428 avis)</span>
  </div>
</div>` 
              }));
            }}
          >
            <i className="fas fa-magic"></i> Exemple
          </button>
        </div>
      </div>
    ) : targetInfo.type === 'selector' ? (
      <div className="selector-input-wrapper">
        <div className="input-with-icon">
          <span className="selector-prefix">#</span>
          <input 
            type="text" 
            value={targetInfo.input}
            onChange={(e) => setTargetInfo(prev => ({ ...prev, input: e.target.value }))}
            placeholder=".product-card, article, #price, h1.title"
            className="selector-input"
          />
        </div>
        <div className="selector-examples">
          <small>Exemples: </small>
          <button 
            className="example-chip"
            onClick={() => setTargetInfo(prev => ({ ...prev, input: '.product-card' }))}
          >
            .product-card
          </button>
          <button 
            className="example-chip"
            onClick={() => setTargetInfo(prev => ({ ...prev, input: 'article' }))}
          >
            article
          </button>
          <button 
            className="example-chip"
            onClick={() => setTargetInfo(prev => ({ ...prev, input: '#price' }))}
          >
            #price
          </button>
        </div>
      </div>
    ) : (
      <div className="url-input-wrapper">
        <div className="input-with-icon">
          <span className="url-prefix">https://</span>
          <input 
            type="text" 
            value={targetInfo.input}
            onChange={(e) => setTargetInfo(prev => ({ ...prev, input: e.target.value }))}
            placeholder="www.exemple.com/page"
            className="url-input-field"
          />
        </div>
        <div className="url-examples">
          <small>Exemples: </small>
          <button 
            className="example-chip"
            onClick={() => setTargetInfo(prev => ({ ...prev, input: 'https://www.amazon.com/electronics' }))}
          >
            amazon.com
          </button>
          <button 
            className="example-chip"
            onClick={() => setTargetInfo(prev => ({ ...prev, input: 'https://themeforest.net' }))}
          >
            themeforest.net
          </button>
          <button 
            className="example-chip"
            onClick={() => setTargetInfo(prev => ({ ...prev, input: 'https://medium.com' }))}
          >
            medium.com
          </button>
        </div>
      </div>
    )}
  </div>
</div>

            {analysis.isComplete && (
              <div className="target-meta">
                <span>
                  <i className="fas fa-bullseye"></i>
                  <strong>Éléments :</strong> {targetInfo.totalElements.toLocaleString()}
                </span>
                <span>
                  <i className="fas fa-chart-line"></i>
                  <strong>Confiance :</strong> {targetInfo.successRate}%
                </span>
                <span>
                  <i className="fas fa-history"></i>
                  <strong>Analyse :</strong> {targetInfo.lastAnalyzed}
                </span>
              </div>
            )}
          </div>
        </section>

        {/* Progression - même que précédemment */}
        {analysis.isLoading && (
          <section className="card">
            <div className="card-header">
              <h4><i className="fas fa-sync-alt fa-spin"></i> Analyse en cours...</h4>
            </div>
            <div className="analysis-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${analysis.progress}%` }}
                ></div>
              </div>
              <div className="progress-steps">
                <div className={`step ${analysis.progress >= 20 ? 'completed' : ''}`}>
                  <div className="step-icon"><i className="fas fa-sitemap"></i></div>
                  <span>Structure</span>
                </div>
                <div className={`step ${analysis.progress >= 40 ? 'completed' : ''}`}>
                  <div className="step-icon"><i className="fas fa-eye"></i></div>
                  <span>Détection</span>
                </div>
                <div className={`step ${analysis.progress >= 60 ? 'completed' : ''}`}>
                  <div className="step-icon"><i className="fas fa-tags"></i></div>
                  <span>Catégorisation</span>
                </div>
                <div className={`step ${analysis.progress >= 80 ? 'completed' : ''}`}>
                  <div className="step-icon"><i className="fas fa-magic"></i></div>
                  <span>Optimisation</span>
                </div>
                <div className={`step ${analysis.progress >= 100 ? 'completed' : ''}`}>
                  <div className="step-icon"><i className="fas fa-check"></i></div>
                  <span>Terminé</span>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Éléments détectés - même que précédemment */}
        {analysis.isComplete && (
          <>
            <section className="card">
              <div className="card-header">
                <h3><i className="fas fa-bullseye"></i> Éléments Détectés</h3>
                <div className="selection-actions">
                  <button 
                    className="btn btn-small"
                    onClick={() => toggleAllElements(true)}
                  >
                    <i className="fas fa-check-double"></i> Tout sélectionner
                  </button>
                  <button 
                    className="btn btn-small btn-secondary"
                    onClick={() => toggleAllElements(false)}
                  >
                    <i className="fas fa-times"></i> Tout désélectionner
                  </button>
                </div>
              </div>

              <div className="elements-grid">
                {detectedElements.map((element) => (
                  <div 
                    key={element.id} 
                    className={`element-card ${element.isSelected ? 'selected' : ''}`}
                    onClick={() => toggleElementSelection(element.id)}
                  >
                    <div className="element-header">
                      <div className="element-icon">
                        <i className={element.icon}></i>
                      </div>
                      <div className="element-title">
                        <h4>{element.name}</h4>
                        <span className="element-count">{element.count} éléments</span>
                      </div>
                      <div className="element-confidence">
                        <div className="confidence-badge">
                          {element.confidence}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="element-body">
                      <p className="element-description">
                        {targetInfo.type === 'html' && element.selector === 'balises' 
                          ? 'Balises HTML détectées'
                          : targetInfo.type === 'html' && element.selector === 'texte'
                          ? 'Contenu texte extrait'
                          : targetInfo.type === 'html' && element.selector === 'attributs'
                          ? 'Attributs HTML'
                          : `Sélecteur: ${element.selector}`}
                      </p>
                    </div>
                    
                    <div className="element-footer">
                      <div className="element-toggle">
                        <div className={`toggle-switch ${element.isSelected ? 'active' : ''}`}>
                          <div className="toggle-slider"></div>
                        </div>
                        <span>{element.isSelected ? 'Sélectionné' : 'Non sélectionné'}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="selection-summary">
                <div className="summary-item">
                  <span className="summary-label">Éléments sélectionnés :</span>
                  <span className="summary-value">
                    {selectedCount} / {detectedElements.length}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Données estimées :</span>
                  <span className="summary-value">
                    {estimatedData.toLocaleString()} éléments
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Confiance moyenne :</span>
                  <span className="summary-value">
                    {averageConfidence}%
                  </span>
                </div>
              </div>
            </section>

            {/* Configuration du scraping - reste identique */}
            <section className="card">
              <div className="card-header">
                <h3><i className="fas fa-cog"></i> Configuration du Scraping</h3>
              </div>

              <div className="scraping-config">
                <div className="config-section">
                  <h4><i className="fas fa-info-circle"></i> Informations du projet</h4>
                  <div className="config-row">
                    <div className="config-field">
                      <label>Nom du projet *</label>
                      <input 
                        type="text" 
                        placeholder={
                          targetInfo.type === 'selector' ? "ex: Scraping sélecteur .product-card" :
                          targetInfo.type === 'html' ? "ex: Scraping HTML structure" :
                          "ex: Scraping Amazon Électronique"
                        }
                        value={scrapingConfig.name}
                        onChange={(e) => setScrapingConfig(prev => ({ 
                          ...prev, 
                          name: e.target.value 
                        }))}
                      />
                    </div>
                  </div>
                </div>

                <div className="config-section">
                  <h4><i className="fas fa-clock"></i> Planification</h4>
                  <div className="config-row">
                    <div className="config-field">
                      <label>Fréquence</label>
                      <select 
                        value={scrapingConfig.schedule}
                        onChange={(e) => setScrapingConfig(prev => ({ 
                          ...prev, 
                          schedule: e.target.value 
                        }))}
                      >
                        <option value="manual">Manuel (une seule fois)</option>
                        <option value="daily">Quotidien</option>
                        <option value="weekly">Hebdomadaire</option>
                                                <option value="monthly">Mensuel</option>
                      </select>
                    </div>
                    
                    <div className="config-field">
                      <label>Profondeur de navigation</label>
                      <select 
                        value={scrapingConfig.depth}
                        onChange={(e) => setScrapingConfig(prev => ({ 
                          ...prev, 
                          depth: parseInt(e.target.value) 
                        }))}
                      >
                        <option value="1">Niveau 1 (page actuelle)</option>
                        <option value="2">Niveau 2 (liens directs)</option>
                        <option value="3">Niveau 3 (2 niveaux de profondeur)</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="config-section">
                  <h4><i className="fas fa-download"></i> Options d'export</h4>
                  <div className="config-row">
                    <div className="config-field">
                      <label>Format de sauvegarde</label>
                      <select 
                        value={scrapingConfig.saveFormat}
                        onChange={(e) => setScrapingConfig(prev => ({ 
                          ...prev, 
                          saveFormat: e.target.value 
                        }))}
                      >
                        <option value="json">JSON (recommandé)</option>
                        <option value="csv">CSV</option>
                        <option value="excel">Excel</option>
                        <option value="both">JSON + CSV</option>
                      </select>
                    </div>
                    
                    {targetInfo.type === 'url' && (
                      <div className="config-field">
                        <label>Pagination automatique</label>
                        <div className="toggle-field">
                          <div 
                            className={`toggle-switch ${scrapingConfig.pagination ? 'active' : ''}`}
                            onClick={() => setScrapingConfig(prev => ({ 
                              ...prev, 
                              pagination: !prev.pagination 
                            }))}
                          >
                            <div className="toggle-slider"></div>
                          </div>
                          <span>Détecter et suivre la pagination</span>
                        </div>
                      </div>
                    )}
                    
                    {targetInfo.type === 'url' && scrapingConfig.pagination && (
                      <div className="config-field">
                        <label>Pages maximum</label>
                        <input 
                          type="number" 
                          min="1" 
                          max="100"
                          value={scrapingConfig.maxPages}
                          onChange={(e) => setScrapingConfig(prev => ({ 
                            ...prev, 
                            maxPages: parseInt(e.target.value) 
                          }))}
                        />
                        <small className="field-hint">Limite pour éviter un scraping infini</small>
                      </div>
                    )}
                  </div>
                </div>

                {/* Configuration spécifique au type d'entrée */}
                <div className="config-section">
                  <h4><i className="fas fa-sliders-h"></i> Paramètres spécifiques</h4>
                  <div className="config-row">
                    {targetInfo.type === 'selector' && (
                      <div className="config-field">
                        <label>Mode de sélection</label>
                        <select 
                          value={scrapingConfig.selectionMode || 'multiple'}
                          onChange={(e) => setScrapingConfig(prev => ({ 
                            ...prev, 
                            selectionMode: e.target.value 
                          }))}
                        >
                          <option value="multiple">Tous les éléments correspondants</option>
                          <option value="first">Premier élément seulement</option>
                          <option value="nth">Élément spécifique (n-ième)</option>
                        </select>
                      </div>
                    )}
                    
                    {targetInfo.type === 'html' && (
                      <div className="config-field">
                        <label>Mode d'extraction HTML</label>
                        <select 
                          value={scrapingConfig.htmlMode || 'structure'}
                          onChange={(e) => setScrapingConfig(prev => ({ 
                            ...prev, 
                            htmlMode: e.target.value 
                          }))}
                        >
                          <option value="structure">Structure complète</option>
                          <option value="content">Contenu texte seulement</option>
                          <option value="both">Structure + contenu</option>
                        </select>
                      </div>
                    )}
                    
                    {/* Adaptateur spécifique au site */}
                    <div className="config-field">
                      <label>Adaptateur de scraping</label>
                      <select 
                        value={scrapingConfig.adapter || 'auto'}
                        onChange={(e) => setScrapingConfig(prev => ({ 
                          ...prev, 
                          adapter: e.target.value 
                        }))}
                      >
                        <option value="auto">Auto-détection</option>
                        <option value="ecommerce">E-commerce (Amazon, eBay)</option>
                        <option value="template">Templates (ThemeForest)</option>
                        <option value="blog">Blogs (Medium, WordPress)</option>
                        <option value="github">GitHub</option>
                        <option value="news">Actualités</option>
                        <option value="generic">Générique</option>
                      </select>
                      <small className="field-hint">
                        {targetInfo.type === 'url' 
                          ? `Détecté: ${detectSiteTypeFromUrl(targetInfo.input)}`
                          : 'Sélectionnez manuellement si besoin'}
                      </small>
                    </div>
                  </div>
                </div>

                {/* Options avancées */}
                <div className="config-section">
                  <h4><i className="fas fa-cogs"></i> Options avancées</h4>
                  <div className="config-row">
                    <div className="config-field">
                      <label>Délai entre les requêtes</label>
                      <select 
                        value={scrapingConfig.delay || 'normal'}
                        onChange={(e) => setScrapingConfig(prev => ({ 
                          ...prev, 
                          delay: e.target.value 
                        }))}
                      >
                        <option value="fast">Rapide (100ms)</option>
                        <option value="normal">Normal (500ms)</option>
                        <option value="slow">Lent (1s)</option>
                        <option value="very-slow">Très lent (2s)</option>
                      </select>
                      <small className="field-hint">Pour éviter le blocage IP</small>
                    </div>
                    
                    <div className="config-field">
                      <label>Proxy</label>
                      <div className="toggle-field">
                        <div 
                          className={`toggle-switch ${scrapingConfig.useProxy || false ? 'active' : ''}`}
                          onClick={() => setScrapingConfig(prev => ({ 
                            ...prev, 
                            useProxy: !prev.useProxy 
                          }))}
                        >
                          <div className="toggle-slider"></div>
                        </div>
                        <span>Utiliser un proxy rotatif</span>
                      </div>
                    </div>
                    
                    {scrapingConfig.useProxy && (
                      <div className="config-field">
                        <label>Service proxy</label>
                        <select 
                          value={scrapingConfig.proxyService || 'none'}
                          onChange={(e) => setScrapingConfig(prev => ({ 
                            ...prev, 
                            proxyService: e.target.value 
                          }))}
                        >
                          <option value="none">Aucun (proxy local)</option>
                          <option value="scrapingbee">ScrapingBee</option>
                          <option value="scraperapi">ScraperAPI</option>
                          <option value="brightdata">Bright Data</option>
                        </select>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>

            {/* Aperçu des données */}
            <section className="card">
              <div className="card-header">
                <h3><i className="fas fa-eye"></i> Aperçu des données à scraper</h3>
              </div>
              <div className="data-preview">
                <div className="preview-header">
                  <div className="preview-stats">
                    <div className="stat">
                      <i className="fas fa-database"></i>
                      <span>{estimatedData.toLocaleString()} éléments estimés</span>
                    </div>
                    <div className="stat">
                      <i className="fas fa-clock"></i>
                      <span>Temps estimé: {calculateEstimatedTime()} secondes</span>
                    </div>
                    <div className="stat">
                      <i className="fas fa-hdd"></i>
                      <span>Taille estimée: {calculateEstimatedSize()} MB</span>
                    </div>
                  </div>
                </div>
                
                <div className="preview-content">
                  <h4>Structure des données générée :</h4>
                  <pre className="json-preview">
                    {generateDataPreview()}
                  </pre>
                  <small className="preview-note">
                    Ceci est une prévisualisation basée sur votre configuration. 
                    Les données réelles peuvent varier.
                  </small>
                </div>
              </div>
            </section>

            {/* Actions */}
            <div className="analysis-actions">
              <button 
                className="btn btn-primary"
                onClick={startScraping}
                disabled={!scrapingConfig.name.trim() || selectedCount === 0}
              >
                <i className="fas fa-play"></i>
                Démarrer le Scraping
              </button>
              
              <button 
                className="btn btn-secondary"
                onClick={exportConfig}
              >
                <i className="fas fa-file-export"></i>
                Exporter la Configuration
              </button>
              
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setTargetInfo(prev => ({ ...prev, input: '', title: '' }));
                  setAnalysis({ isLoading: false, isComplete: false, progress: 0, error: null });
                  setDetectedElements([]);
                }}
              >
                <i className="fas fa-redo"></i>
                Nouvelle Analyse
              </button>
              
              <Link to="/dashboard" className="btn btn-secondary">
                <i className="fas fa-arrow-left"></i>
                Retour au Dashboard
              </Link>
            </div>
          </>
        )}

        {/* État vide */}
        {!analysis.isLoading && !analysis.isComplete && (
          <section className="card">
            <div className="empty-state">
              <div className="empty-icon">
                <i className="fas fa-search"></i>
              </div>
              <h3>Prêt à analyser</h3>
              <p>
                {targetInfo.type === 'selector' 
                  ? 'Entrez un sélecteur CSS pour analyser les éléments correspondants'
                  : targetInfo.type === 'html'
                  ? 'Collez du HTML brut à analyser'
                  : 'Entrez une URL pour analyser le site web'}
              </p>
              
              <div className="example-inputs">
                <h4>Exemples :</h4>
                <div className="example-grid">
                  {targetInfo.type === 'url' && (
                    <>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ ...prev, input: 'https://www.amazon.com/electronics' }));
                        }}
                      >
                        <i className="fas fa-shopping-cart"></i>
                        Amazon Electronics
                      </button>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ ...prev, input: 'https://themeforest.net' }));
                        }}
                      >
                        <i className="fas fa-palette"></i>
                        ThemeForest
                      </button>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ ...prev, input: 'https://medium.com' }));
                        }}
                      >
                        <i className="fas fa-blog"></i>
                        Medium
                      </button>
                    </>
                  )}
                  
                  {targetInfo.type === 'selector' && (
                    <>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ ...prev, input: '.product-card' }));
                        }}
                      >
                        <i className="fas fa-box"></i>
                        Produits E-commerce
                      </button>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ ...prev, input: 'article' }));
                        }}
                      >
                        <i className="fas fa-newspaper"></i>
                        Articles de blog
                      </button>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ ...prev, input: '#price' }));
                        }}
                      >
                        <i className="fas fa-tag"></i>
                        Prix
                      </button>
                    </>
                  )}
                  
                  {targetInfo.type === 'html' && (
                    <>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ 
                            ...prev, 
                            input: '<div class="product"><h3>iPhone 15 Pro</h3><p class="price">1099€</p></div>' 
                          }));
                        }}
                      >
                        <i className="fas fa-mobile"></i>
                        Produit HTML
                      </button>
                      <button 
                        className="example-btn"
                        onClick={() => {
                          setTargetInfo(prev => ({ 
                            ...prev, 
                            input: '<article><h2>Titre Article</h2><p>Contenu intéressant...</p></article>' 
                          }));
                        }}
                      >
                        <i className="fas fa-file-alt"></i>
                        Article HTML
                      </button>
                    </>
                  )}
                </div>
              </div>
              
              <div className="empty-actions">
                <button 
                  className="btn btn-primary"
                  onClick={() => navigate('/dashboard')}
                >
                  <i className="fas fa-arrow-left"></i>
                  Retour au Dashboard
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => {
                    const types = ['url', 'selector', 'html'];
                    const nextType = types[(types.indexOf(targetInfo.type) + 1) % types.length];
                    setTargetInfo(prev => ({ ...prev, type: nextType, input: '' }));
                  }}
                >
                  <i className="fas fa-exchange-alt"></i>
                  Changer de type
                </button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );

  // Fonctions utilitaires additionnelles
  function calculateEstimatedTime() {
    const baseTime = targetInfo.type === 'url' 
      ? estimatedData * (scrapingConfig.delay === 'fast' ? 0.1 : 
                        scrapingConfig.delay === 'normal' ? 0.5 : 
                        scrapingConfig.delay === 'slow' ? 1 : 2)
      : 0.5;
    
    return Math.max(1, Math.round(baseTime));
  }

  function calculateEstimatedSize() {
    const bytesPerElement = targetInfo.type === 'html' ? 500 : 200;
    const totalBytes = estimatedData * bytesPerElement;
    return (totalBytes / (1024 * 1024)).toFixed(2);
  }

  function generateDataPreview() {
    const selectedElements = detectedElements.filter(el => el.isSelected);
    
    if (selectedElements.length === 0) {
      return JSON.stringify({ message: "Aucun élément sélectionné" }, null, 2);
    }
    
    const preview = {
      metadata: {
        project: scrapingConfig.name,
        type: targetInfo.type,
        url: targetInfo.type === 'url' ? targetInfo.input : undefined,
        selector: targetInfo.type === 'selector' ? targetInfo.input : undefined,
        timestamp: new Date().toISOString(),
        elementsCount: estimatedData
      },
      data: selectedElements.map(el => ({
        name: el.name,
        selector: el.selector,
        count: el.count,
        confidence: el.confidence,
        sampleData: generateSampleData(el.name, targetInfo.type)
      }))
    };
    
    return JSON.stringify(preview, null, 2);
  }

  function generateSampleData(elementName, type) {
    const samples = {
      'Produits': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'Google Pixel 8'],
      'Prix': ['999€', '1,299€', '899€'],
      'Images': ['product-image-1.jpg', 'product-image-2.jpg'],
      'Articles': ['Introduction à React', 'Guide de scraping web', 'Nouvelles fonctionnalités'],
      'Titres': ['Titre principal', 'Sous-titre important', 'Section 1'],
      'Auteurs': ['Jean Dupont', 'Marie Martin', 'Alexandre Bernard'],
      'Dates': ['2024-01-15', '2024-01-14', '2024-01-13'],
      'Répositories': ['react', 'vue', 'next.js'],
      'Stars': ['245', '189', '542'],
      'Templates': ['Business Pro', 'Creative Portfolio', 'E-commerce Suite']
    };
    
    return samples[elementName] || ['Donnée 1', 'Donnée 2', 'Donnée 3'];
  }
};

export default Analysis;