// Location: C:\Users\Admin\Downloads\scrapping.web\scrapping.web\scraper-pro\frontend\src\pages\Analysis\Analysis.jsx
// Component for website analysis and scraping configuration
// Allows users to input URL, view auto-detected content types, configure scraping options
// RELEVANT FILES: App.jsx, AuthContext.jsx, analysis.css, Results.jsx

import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../../services/api';
import { useScraping } from '../../contexts/ScrapingContext';


export default function Analysis() {
  const navigate = useNavigate();
  const location = useLocation();
  const { 
    startScrapingTask, 
    startBatchScrapingTask,
    startAnalysisTask, 
    isScrapingInProgress, 
    isAnalysisInProgress,
    addNotification,
    activeTasks,
    getCompletedAnalysis,
  } = useScraping();
  
  // State management
  const [url, setUrl] = useState('');
  const [isBatchMode, setIsBatchMode] = useState(false);
  const [batchUrls, setBatchUrls] = useState('');
  const [screenshot, setScreenshot] = useState(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [includeSubdomains, setIncludeSubdomains] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [sessionId, setSessionId] = useState(null);
  
  // Analysis results
  const [siteInfo, setSiteInfo] = useState({
    domain: '',
    pageCount: 0,
    contentTypesCount: 0
  });
  
  // Subdomain results
  const [subdomains, setSubdomains] = useState({
    scrapable: [],
    nonScrapable: [],
    total: 0
  });
  
  // Paths/directories results
  const [paths, setPaths] = useState({
    discovered: [],
    total: 0,
    sources: []
  });
  
  // Content type selection
  const [selectedTypes, setSelectedTypes] = useState([]);
  const [contentTypes, setContentTypes] = useState([]);
  const [scrapableContent, setScrapableContent] = useState(null);
  const [selectedScrapableTypes, setSelectedScrapableTypes] = useState([]);
  const [expandedScrapable, setExpandedScrapable] = useState(null);
  
  // Advanced options
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [advancedOptions, setAdvancedOptions] = useState({
    depth: '2',
    delay: '500',
    userAgent: 'Chrome (Desktop)',
    timeout: '30',
    max_pages: ''
  });
  
  // Custom selectors
  const [customSelectors, setCustomSelectors] = useState([
    { name: 'Titre produit', selector: 'h2.product-title' },
    { name: 'Prix', selector: 'span.price' }
  ]);
  
  // Selected pages from analysis
  const [selectedPages, setSelectedPages] = useState(new Set());
  const [activePreviewPage, setActivePreviewPage] = useState(null);

  // Storage format
  const [selectedFormat, setSelectedFormat] = useState('json');
  const [includeImagesZip, setIncludeImagesZip] = useState(false);
  const formats = [
    { id: 'json', icon: '🔧', name: 'JSON' },
    { id: 'csv', icon: '📄', name: 'CSV' },
    { id: 'excel', icon: '📊', name: 'Excel' },
    { id: 'pdf', icon: '📕', name: 'PDF' },
    { id: 'xml', icon: '📋', name: 'XML' }
  ];
  
  // Output formats (like Firecrawl)
  const [outputFormats, setOutputFormats] = useState({
    markdown: true,
    summary: true,
    links: true,
    html: true,
    screenshot: true,
    json: true,
    branding: false,
    images: true
  });
  
  const [htmlMode, setHtmlMode] = useState('cleaned'); // 'cleaned' or 'raw'
  const [screenshotMode, setScreenshotMode] = useState('viewport'); // 'viewport' or 'fullpage'
  
  const [showFormatModal, setShowFormatModal] = useState(false);
  
  // Vérifier si une analyse en cours est terminée (quand on revient sur la page)
  useEffect(() => {
    // Chercher une tâche d'analyse terminée pour cette URL
    const completedTask = activeTasks.find(t => 
      t.type === 'analysis' && 
      t.status === 'completed' && 
      t.results
    );
    
    if (completedTask && completedTask.results) {
      // Une analyse est terminée, charger les résultats
      handleAnalysisComplete(completedTask.results);
      setUrl(completedTask.url);
      setSessionId(completedTask.sessionId);
    }
  }, [activeTasks]);
  
  // Normalize URL (add https:// if missing)
  const normalizeUrl = (urlString) => {
    urlString = urlString.trim();
    if (!urlString.startsWith('http://') && !urlString.startsWith('https://')) {
      return `https://${urlString}`;
    }
    return urlString;
  };
  
  // Validate URL
  const isValidUrl = (urlString) => {
    try {
      new URL(urlString);
      return true;
    } catch (e) {
      return false;
    }
  };
  
  // Get list of URLs from batch textarea
  const getBatchUrlList = () => {
    return batchUrls
      .split('\n')
      .map(u => u.trim())
      .filter(u => u.length > 0)
      .map(u => normalizeUrl(u));
  };

  // Handle Batch Configuration (Skip Analysis)
   const handleConfigureBatch = () => {
     const urls = getBatchUrlList();
     if (urls.length === 0) {
       alert('Veuillez entrer au moins une URL');
       return;
     }
     
     // Check if valid URLs
     const invalidUrls = urls.filter(u => !isValidUrl(u));
     if (invalidUrls.length > 0) {
       alert(`Certaines URLs sont invalides : \n${invalidUrls.slice(0, 3).join('\n')}${invalidUrls.length > 3 ? '...' : ''}`);
       return;
     }
     
     // Set first URL as main URL for site info
     const mainUrl = urls[0];
     setUrl(mainUrl);
     
     // Mock site info
     try {
       const domain = new URL(mainUrl).hostname;
       setSiteInfo({
         domain: domain,
         pageCount: urls.length,
         contentTypesCount: 5 // Default types
       });
     } catch (e) {
       // Ignore
     }
     
     // Default content types for batch mode
     const defaultTypes = [
       { id: 'text_content', icon: '📝', title: 'Texte', description: 'Contenu textuel principal', count: 'Auto' },
       { id: 'media', icon: '🖼️', title: 'Médias', description: 'Images et vidéos', count: 'Auto' },
       { id: 'links', icon: '🔗', title: 'Liens', description: 'Tous les liens', count: 'Auto' },
       { id: 'tables', icon: '📊', title: 'Tableaux', description: 'Tableaux de données', count: 'Auto' },
       { id: 'metadata', icon: '📋', title: 'Métadonnées', description: 'Titre, description, mots-clés', count: 'Auto' },
     ];
     setContentTypes(defaultTypes);
     // Pre-select text and media
     setSelectedTypes(['text_content', 'media']);
     
     // Skip to configuration
     setCurrentStep(4);
     setShowResults(true); 
   };
  
  // Handle URL analysis - Mode ASYNCHRONE
  const handleAnalyze = async () => {
    if (!url) {
      alert('Veuillez entrer une URL');
      return;
    }
    
    // Normaliser l'URL (ajouter https:// si nécessaire)
    const normalizedUrl = normalizeUrl(url);
    setUrl(normalizedUrl);
    
    if (!isValidUrl(normalizedUrl)) {
      alert('Veuillez entrer une URL valide');
      return;
    }
    
    setIsAnalyzing(true);
    setCurrentStep(2);
    
    try {
      // Lancer l'analyse en arrière-plan via le contexte
      const result = await startAnalysisTask(normalizedUrl, includeSubdomains, (completionResult) => {
        // Callback appelé quand l'analyse est terminée
        if (completionResult.success) {
          console.log('Analyse terminée avec succès:', completionResult.results);
          // Traiter les résultats
          handleAnalysisComplete(completionResult.results);
        } else {
          console.error('Analyse échouée:', completionResult.error);
          setCurrentStep(1);
          setIsAnalyzing(false);
        }
      });
      
      // Enregistrer le session_id
      if (result.sessionId) {
        setSessionId(result.sessionId);
        
        // Mettre à jour les infos du site
        const domain = new URL(normalizedUrl).hostname;
        setSiteInfo({
          domain: domain,
          pageCount: 0,
          contentTypesCount: 0
        });
      }
      
      // L'utilisateur peut maintenant naviguer ailleurs
      // La notification le préviendra quand l'analyse sera terminée
      
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
      alert(`Erreur lors de l'analyse de l'URL: ${error.message || 'Erreur inconnue'}`);
      setCurrentStep(1);
      setIsAnalyzing(false);
    }
  };
  
  // Callback appelé quand l'analyse est terminée
  const handleAnalysisComplete = (results) => {
    console.log('Analyse terminée, résultats:', results);
    
    // Récupérer l'URL depuis les résultats ou la variable locale
    const analysisUrl = results.url || url;
    
    if (!analysisUrl) {
      console.error('URL manquante dans les résultats');
      return;
    }
    
    // Mettre à jour l'URL si elle n'était pas définie
    if (!url && analysisUrl) {
      setUrl(analysisUrl);
    }
    
    // Mettre à jour les infos du site
    let domain;
    try {
      domain = new URL(analysisUrl).hostname;
    } catch (e) {
      console.error('URL invalide:', analysisUrl, e);
      domain = analysisUrl;
    }
    
    setSiteInfo({
      domain: domain,
      pageCount: results.page_count || 0,
      contentTypesCount: results.content_types?.length || 0
    });
    
    // Mettre à jour les types de contenu
    if (results.content_types && results.content_types.length > 0) {
      setContentTypes(results.content_types);
    }
    
    // Mettre à jour les contenus scrapables détectés
    if (results.scrapable_content) {
      setScrapableContent(results.scrapable_content);
    }
    
    // Mettre à jour les sous-domaines
    if (results.subdomains) {
      const scrapableList = results.subdomains.scrapable_list || [];
      const allSubdomains = results.subdomains.all_subdomains || [];
      const checkDetails = results.subdomains.check_details || {};
      
      const nonScrapableList = allSubdomains.filter(
        subdomain => !scrapableList.includes(subdomain)
      );
      
      setSubdomains({
        scrapable: scrapableList.map(sub => ({
          url: sub,
          status: checkDetails[sub]?.status || 'unknown',
          protection: checkDetails[sub]?.protection || null,
          tech_stack: checkDetails[sub]?.tech_stack || []
        })),
        nonScrapable: nonScrapableList.map(sub => ({
          url: sub,
          status: checkDetails[sub]?.status || 'unknown',
          protection: checkDetails[sub]?.protection || null,
          tech_stack: checkDetails[sub]?.tech_stack || []
        })),
        total: allSubdomains.length,
        totalFound: results.subdomains.total_found || 0,
        sources: results.subdomains.sources || []
      });
    }
    
    // Mettre à jour les chemins
    if (results.paths) {
      const discoveredPaths = results.paths.paths || [];
      const mainPages = results.paths.main_pages || [];
      const allPages = results.paths.all_pages || [];
      
      setPaths({
        discovered: discoveredPaths,
        mainPages: mainPages,
        allPages: allPages,
        navigation: results.paths.navigation || {},
        pagesCrawled: results.paths.pages_crawled || 0,
        total: results.paths.total_found || 0
      });
      
      // Auto-select first page for preview
       if (allPages.length > 0) {
         setActivePreviewPage(allPages[0]);
       } else if (mainPages.length > 0) {
         setActivePreviewPage(mainPages[0]);
       } else if (discoveredPaths.length > 0) {
          setActivePreviewPage({ url: discoveredPaths[0], title: discoveredPaths[0], preview: null });
       } else {
         setActivePreviewPage(null);
       }
    }
    
    // Afficher les résultats
    setShowResults(true);
    setCurrentStep(3);
    setIsAnalyzing(false);
  };

  const handlePreview = async () => {
    if (!url) {
      addNotification({ type: 'error', title: 'URL manquante', message: 'Veuillez entrer une URL pour la prévisualisation.' });
      return;
    }
    const normalizedUrl = normalizeUrl(url);
    if (!isValidUrl(normalizedUrl)) {
      addNotification({ type: 'error', title: 'URL invalide', message: 'Veuillez entrer une URL valide.' });
      return;
    }
    
    setIsPreviewLoading(true);
    setScreenshot(null);
    
    try {
      const response = await api.post('/analysis/preview/', { url: normalizedUrl });
      if (response.data.screenshot) {
        setScreenshot(response.data.screenshot);
      } else {
        throw new Error(response.data.error || 'La capture d\'écran n\'a pas pu être générée.');
      }
    } catch (error) {
      console.error('Erreur lors de la prévisualisation:', error);
      addNotification({ type: 'error', title: 'Erreur de prévisualisation', message: error.message || 'Une erreur est survenue.' });
    } finally {
      setIsPreviewLoading(false);
    }
  };

  
  // Toggle content type selection
  const toggleContentType = (typeId) => {
    setSelectedTypes(prev => 
      prev.includes(typeId) 
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    );
  };
  
  // Add custom selector
  const addCustomSelector = () => {
    setCustomSelectors([...customSelectors, { name: '', selector: '' }]);
  };
  
  // Remove custom selector
  const removeCustomSelector = (index) => {
    setCustomSelectors(customSelectors.filter((_, i) => i !== index));
  };
  
  // Update custom selector
  const updateCustomSelector = (index, field, value) => {
    const updated = [...customSelectors];
    updated[index][field] = value;
    setCustomSelectors(updated);
  };
  
  // Toggle page selection
  const togglePageSelection = (pageUrl) => {
    const newSelection = new Set(selectedPages);
    if (newSelection.has(pageUrl)) {
      newSelection.delete(pageUrl);
    } else {
      newSelection.add(pageUrl);
    }
    setSelectedPages(newSelection);
  };

  // Toggle all pages
  const toggleAllPages = (allPages) => {
    if (!allPages || allPages.length === 0) return;
    
    if (selectedPages.size === allPages.length) {
      setSelectedPages(new Set());
    } else {
      setSelectedPages(new Set(allPages.map(p => p.url)));
    }
  };

  // Start scraping
  const handleStartScraping = async () => {
    if (selectedTypes.length === 0) {
      alert('Veuillez sélectionner au moins un type de contenu à extraire');
      return;
    }
    
    try {
      setCurrentStep(4);
      
      // Préparer la configuration du scraping
      const config = {
        url: url,
        include_subdomains: includeSubdomains,
        content_types: selectedTypes,
        depth: parseInt(advancedOptions.depth) || 2,
        delay: parseInt(advancedOptions.delay) || 500,
        user_agent: advancedOptions.userAgent,
        timeout: parseInt(advancedOptions.timeout) || 30,
        max_pages: advancedOptions.max_pages ? parseInt(advancedOptions.max_pages) : null,
        custom_selectors: customSelectors.filter(s => s.name && s.selector),
        output_format: selectedFormat,
        include_images_zip: includeImagesZip
      };
      
      // Handle Batch Mode (Manual Input)
      if (isBatchMode) {
        const urls = getBatchUrlList();
        if (urls.length === 0) {
           alert('Veuillez entrer au moins une URL');
           return;
        }
        
        // Use first URL as main URL for config/display
        config.url = urls[0];
        
        const result = await startBatchScrapingTask(urls, config, (completionResult) => {
          // Callback appelé quand le scraping est terminé
          if (completionResult.success) {
            console.log('Scraping par lot terminé avec succès:', completionResult.sessionId);
          } else {
            console.error('Scraping par lot échoué:', completionResult.error);
          }
        });
        
        // Rediriger vers le dashboard ou rester ici
        addNotification({
          type: 'info',
          title: '🚀 Scraping par lot lancé !',
          message: `Vous pouvez naviguer librement. Session #${result.sessionId}`,
          sessionId: result.sessionId,
        });
        
        // Rediriger directement vers le dashboard pour voir la progression
        navigate('/dashboard');
        
        return; // Stop here for batch mode
      }
      
      // Handle Selected Pages from Analysis (Treat as Batch)
      if (selectedPages.size > 0) {
         const urls = Array.from(selectedPages);
         
         // Use main URL or first selected URL for config
         config.url = urls[0];
         
         const result = await startBatchScrapingTask(urls, config, (completionResult) => {
           if (completionResult.success) {
             console.log('Scraping sélectif terminé avec succès:', completionResult.sessionId);
           } else {
             console.error('Scraping sélectif échoué:', completionResult.error);
           }
         });
         
         addNotification({
           type: 'info',
           title: '🚀 Scraping sélectif lancé !',
           message: `Extraction de ${urls.length} pages sélectionnées. Session #${result.sessionId}`,
           sessionId: result.sessionId,
         });
         
         navigate('/dashboard');
         return;
      }
      
      // Single URL Mode (Full Crawl)
      // Lancer le scraping en arrière-plan via le contexte
      const result = await startScrapingTask(url, config, (completionResult) => {
        // Callback appelé quand le scraping est terminé
        if (completionResult.success) {
          console.log('Scraping terminé avec succès:', completionResult.sessionId);
        } else {
          console.error('Scraping échoué:', completionResult.error);
        }
      });
      
      // Rediriger vers le dashboard ou rester ici - l'utilisateur peut naviguer librement
      addNotification({
        type: 'info',
        title: '🚀 Scraping lancé !',
        message: `Vous pouvez naviguer librement. Session #${result.sessionId}`,
        sessionId: result.sessionId,
      });
      
      // Rediriger directement vers le dashboard pour voir la progression
      navigate('/dashboard');
      
    } catch (error) {
      console.error('Erreur lors du démarrage du scraping:', error);
      setCurrentStep(3);
    }
  };
  
  // Calculate step progress
  const getStepProgress = () => {
    switch(currentStep) {
      case 1: return '25%';
      case 2: return '50%';
      case 3: return '75%';
      case 4: return '100%';
      default: return '25%';
    }
  };
  
  return (
    <div className="analysis-page-container">
      {/* Colonne de gauche pour les étapes (interne) */}
      <div className="analysis-steps-sidebar">
        <h2 className="analysis-internal-title">NOUVELLE ANALYSE</h2>
        <div className="step-indicator-vertical">
          <div className={`step ${currentStep >= 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
            <div className="step-number">{currentStep > 1 ? '✓' : '1'}</div>
            <div className="step-label">URL du site</div>
          </div>
          <div className={`step ${currentStep >= 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
            <div className="step-number">{currentStep > 2 ? '✓' : '2'}</div>
            <div className="step-label">Analyse auto</div>
          </div>
          <div className={`step ${currentStep >= 3 ? 'active' : ''} ${currentStep > 3 ? 'completed' : ''}`}>
            <div className="step-number">{currentStep > 3 ? '✓' : '3'}</div>
            <div className="step-label">Sélection</div>
          </div>
          <div className={`step ${currentStep >= 4 ? 'active' : ''}`}>
            <div className="step-number">4</div>
            <div className="step-label">Configuration</div>
          </div>
        </div>
      </div>

      {/* Colonne de droite pour le contenu principal (interne) */}
      <div className="analysis-content-area">
        {/* Le Header global gère déjà le titre principal, on l'omet ici ou on garde juste le sous-titre si besoin */}
        
        {/* Step 1: URL Input */}
        {!showResults && (
          <div className="analysis-step-1-grid">
            <div className="card analysis-card">
              <div className="card-body">
                <div className="form-group">
                  <label htmlFor="urlInput" className="form-label">URL du site web</label>
                  <div className="input-with-icon-and-button">
                    <span className="material-icons input-icon">link</span>
                    <input
                      type="text"
                      id="urlInput"
                      className="form-control"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      placeholder="https://exemple.com"
                      onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                    />
                  </div>
                </div>
                
                <div className="form-group-inline">
                  <div className="checkbox-group">
                    <input
                      type="checkbox"
                      id="includeSubdomains"
                      checked={includeSubdomains}
                      onChange={(e) => setIncludeSubdomains(e.target.checked)}
                    />
                    <label htmlFor="includeSubdomains" className="checkbox-label">
                      <span className="checkbox-title">Inclure les sous-domaines</span>
                      <span className="checkbox-description">Scraper également les sous-domaines du site principal</span>
                    </label>
                  </div>
                </div>
                
                <div className="form-actions">
                  <button
                    className="btn btn-primary"
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                  >
                    <span className="material-icons">{isAnalyzing ? 'hourglass_empty' : 'rocket_launch'}</span>
                    {isAnalyzing ? 'Analyse en cours...' : 'Analyser le site'}
                  </button>
                </div>
              </div>
              
              {/* Message informatif pendant l'analyse asynchrone */}
              {isAnalyzing && sessionId && (
                <div className="async-analysis-info">
                  <div className="spinner"></div>
                  <h3>Analyse en cours...</h3>
                  <p>
                    L'analyse se poursuit en arrière-plan. Vous pouvez naviguer librement, 
                    une notification vous préviendra quand c'est terminé.
                  </p>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => navigate('/dashboard')}
                  >
                    Aller au Dashboard
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Step 2 & 3: Analysis Results */}
        {showResults && (
          <div className="analysis-results visible">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">
                  <span>✨</span>
                  Analyse terminée !
                </h2>
                <p className="card-description">
                  Voici ce que nous avons trouvé sur ce site. Cochez les éléments que vous souhaitez extraire.
                </p>
              </div>
              
              {/* Site Info */}
              <div className="site-info-card">
                <div className="site-info-grid">
                  <div className="info-item">
                    <span className="info-label">{isBatchMode ? 'Mode' : 'Domaine'}</span>
                    <span className="info-value">{isBatchMode ? 'Scraping par lot' : siteInfo.domain}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">{isBatchMode ? 'URLs à traiter' : 'Pages détectées'}</span>
                    <span className="info-value" style={{ color: 'var(--accent)' }}>
                      {siteInfo.pageCount}
                    </span>
                  </div>
                  {!isBatchMode && (
                  <div className="info-item">
                    <span className="info-label">Types de contenu</span>
                    <span className="info-value" style={{ color: 'var(--success)' }}>
                      {siteInfo.contentTypesCount}
                    </span>
                  </div>
                  )}
                </div>
              </div>
              
              <div className="analysis-split-view" style={{ 
                display: 'flex', 
                gap: '0', 
                borderTop: '1px solid var(--border-color)',
                height: '600px', // Fixed height for scrolling
                position: 'relative'
              }}>
                
                {/* Left Pane: Navigation & List */}
                <div className="analysis-list-pane" style={{ 
                  width: '40%', 
                  minWidth: '320px', 
                  overflowY: 'auto', 
                  borderRight: '1px solid var(--border-color)',
                  padding: '1rem'
                }}>

              {/* Subdomains Section */}
              {!isBatchMode && includeSubdomains && subdomains.total > 0 && (
                <div className="subdomains-section">
                  <h3 className="section-title">
                    <span>🌐</span>
                    Sous-domaines découverts ({subdomains.total})
                  </h3>
                  
                  {/* Scrapable Subdomains */}
                  {subdomains.scrapable.length > 0 && (
                    <div className="subdomain-group">
                      <h4 className="subdomain-group-title">
                        <span className="status-badge success">✓</span>
                        Scrapables ({subdomains.scrapable.length})
                      </h4>
                      <div className="subdomain-list">
                        {subdomains.scrapable.map((sub, idx) => (
                          <div key={idx} className="subdomain-item scrapable">
                            <div className="subdomain-url">
                              <span className="subdomain-icon">✅</span>
                              <span>{sub.url}</span>
                            </div>
                            <div className="subdomain-meta">
                              <span className="status-code">{sub.status}</span>
                              {sub.tech_stack.length > 0 && (
                                <span className="tech-stack">
                                  {sub.tech_stack.slice(0, 2).join(', ')}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Non-Scrapable Subdomains */}
                  {subdomains.nonScrapable.length > 0 && (
                    <div className="subdomain-group">
                      <h4 className="subdomain-group-title">
                        <span className="status-badge warning">⚠</span>
                        Non-scrapables ({subdomains.nonScrapable.length})
                      </h4>
                      <div className="subdomain-list">
                        {subdomains.nonScrapable.map((sub, idx) => (
                          <div key={idx} className="subdomain-item non-scrapable">
                            <div className="subdomain-url">
                              <span className="subdomain-icon">
                                {sub.status >= 500 ? '❌' : '🚫'}
                              </span>
                              <span>{sub.url}</span>
                            </div>
                            <div className="subdomain-meta">
                              <span className="status-code error">{sub.status}</span>
                              {sub.protection && (
                                <span className="protection-badge">
                                  🛡️ {sub.protection}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Paths/Directories Section */}
              {!isBatchMode && paths.total > 0 && (
                <div className="paths-section">
                  <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 className="section-title" style={{ margin: 0 }}>
                      <span>📂</span>
                      Pages découvertes ({paths.total}) - {paths.pagesCrawled} pages crawlées
                    </h3>
                    <button 
                      className="btn btn-sm btn-outline" 
                      onClick={() => toggleAllPages(paths.allPages || paths.discovered.map(u => ({url: u})))}
                      style={{ fontSize: '0.8rem', padding: '0.25rem 0.5rem' }}
                    >
                      {selectedPages.size > 0 && selectedPages.size === (paths.allPages?.length || paths.discovered?.length) 
                        ? 'Tout désélectionner' 
                        : 'Tout sélectionner'}
                    </button>
                  </div>
                  
                  {/* Selection Info */}
                  {selectedPages.size > 0 && (
                    <div className="selection-info" style={{ 
                      background: 'rgba(var(--primary-rgb), 0.1)', 
                      padding: '0.5rem 1rem', 
                      borderRadius: '4px', 
                      margin: '1rem 0',
                      border: '1px solid var(--primary)',
                      color: 'var(--primary)',
                      fontWeight: '500',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span>{selectedPages.size} page(s) sélectionnée(s) pour l'extraction</span>
                      <button 
                        onClick={() => setSelectedPages(new Set())}
                        style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', textDecoration: 'underline', fontSize: '0.85rem' }}
                      >
                        Effacer
                      </button>
                    </div>
                  )}
                  
                  {/* Main Navigation Pages */}
                  {paths.mainPages && paths.mainPages.length > 0 && (
                    <div className="main-pages-group">
                      <h4 className="subdomain-group-title">
                        <span className="status-badge success">⭐</span>
                        Pages principales ({paths.mainPages.length})
                      </h4>
                      <div className="paths-list">
                        {paths.mainPages.map((page, idx) => (
                          <div 
                            key={idx} 
                            className={`path-item main-page ${selectedPages.has(page.url) ? 'selected' : ''} ${activePreviewPage?.url === page.url ? 'active-preview' : ''}`}
                            onClick={(e) => {
                              // If clicking checkbox/wrapper, toggle selection
                              if (e.target.type === 'checkbox' || e.target.closest('.checkbox-wrapper')) {
                                togglePageSelection(page.url);
                              } else {
                                // Otherwise set preview
                                setActivePreviewPage(page);
                              }
                            }}
                            style={{ 
                              cursor: 'pointer',
                              border: activePreviewPage?.url === page.url ? '1px solid var(--primary)' : (selectedPages.has(page.url) ? '1px solid var(--primary)' : '1px solid var(--border-color)'),
                              background: activePreviewPage?.url === page.url ? 'rgba(var(--primary-rgb), 0.1)' : (selectedPages.has(page.url) ? 'rgba(var(--primary-rgb), 0.05)' : 'var(--card-bg)'),
                              position: 'relative'
                            }}
                          >
                            <div className="checkbox-wrapper" style={{ marginRight: '0.75rem', display: 'flex', alignItems: 'center', zIndex: 2 }}>
                              <input 
                                type="checkbox" 
                                checked={selectedPages.has(page.url)} 
                                readOnly 
                                style={{ transform: 'scale(1.2)', cursor: 'pointer' }}
                              />
                            </div>
                            <span className="path-icon">🔗</span>
                            <div className="path-details" style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflow: 'hidden', flex: 1 }}>
                              <span className="path-text" style={{ fontWeight: '500', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{page.text || 'Sans titre'}</span>
                              <span className="path-url" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{page.url}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* All Discovered Paths with Previews */}
                  {paths.allPages && paths.allPages.length > 0 && (
                    <div className="all-paths-group">
                      <h4 className="subdomain-group-title">
                        <span className="status-badge">📄</span>
                        Toutes les pages découvertes ({paths.allPages.length})
                      </h4>
                      <div className="paths-list">
                        {paths.allPages.map((page, idx) => (
                          <div 
                            key={idx} 
                            className={`path-item-with-preview ${selectedPages.has(page.url) ? 'selected' : ''} ${activePreviewPage?.url === page.url ? 'active-preview' : ''}`}
                            onClick={(e) => {
                                // If clicking checkbox/wrapper, toggle selection
                                if (e.target.type === 'checkbox' || e.target.closest('.selection-indicator')) {
                                  togglePageSelection(page.url);
                                } else {
                                  // Otherwise set preview
                                  setActivePreviewPage(page);
                                }
                            }}
                            style={{ 
                              cursor: 'pointer',
                              border: activePreviewPage?.url === page.url ? '1px solid var(--primary)' : (selectedPages.has(page.url) ? '1px solid var(--primary)' : '1px solid var(--border-color)'),
                              background: activePreviewPage?.url === page.url ? 'rgba(var(--primary-rgb), 0.1)' : 'var(--card-bg)',
                              position: 'relative',
                              padding: '0.75rem',
                              borderRadius: '8px',
                              marginBottom: '0.5rem',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.75rem'
                            }}
                          >
                            <div className="selection-indicator" style={{
                              marginRight: '0.5rem'
                            }}>
                              <input 
                                type="checkbox" 
                                checked={selectedPages.has(page.url)} 
                                readOnly 
                                style={{ transform: 'scale(1.2)', cursor: 'pointer' }}
                              />
                            </div>
                            
                            <span className="path-icon">📄</span>
                            <div className="path-details" style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflow: 'hidden', flex: 1 }}>
                              <span className="path-text" style={{ fontWeight: '500', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{page.title || 'Sans titre'}</span>
                              <span className="path-url" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {page.url}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* All Discovered Paths (simple list) */}
                  {paths.discovered && paths.discovered.length > 0 && (
                    <div className="all-paths-group" style={{ marginTop: '2rem' }}>
                      <h4 className="subdomain-group-title" style={{ fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="status-badge" style={{ fontSize: '1.2rem' }}>📄</span>
                        Tous les chemins ({paths.discovered.length})
                      </h4>
                      <div className="paths-list" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {paths.discovered.map((path, idx) => (
                          <div 
                            key={idx} 
                            className={`path-item ${selectedPages.has(path) ? 'selected' : ''}`}
                            onClick={(e) => {
                              // If clicking checkbox/wrapper, toggle selection
                              if (e.target.type === 'checkbox' || e.target.closest('.checkbox-wrapper')) {
                                togglePageSelection(path);
                              } else {
                                // Otherwise set preview
                                setActivePreviewPage({
                                  url: path,
                                  title: path,
                                  preview: null
                                });
                              }
                            }}
                            style={{ 
                              cursor: 'pointer',
                              border: activePreviewPage?.url === path ? '1px solid var(--primary)' : (selectedPages.has(path) ? '1px solid var(--primary)' : '1px solid var(--border-color)'),
                              background: activePreviewPage?.url === path ? 'rgba(var(--primary-rgb), 0.1)' : (selectedPages.has(path) ? 'rgba(var(--primary-rgb), 0.05)' : 'var(--card-bg)'),
                              display: 'flex',
                              alignItems: 'center',
                              padding: '0.75rem',
                              borderRadius: '6px',
                              transition: 'all 0.2s ease'
                            }}
                          >
                            <div className="checkbox-wrapper" style={{ marginRight: '0.75rem', display: 'flex', alignItems: 'center' }}>
                              <input 
                                type="checkbox" 
                                checked={selectedPages.has(path)} 
                                readOnly 
                                style={{ transform: 'scale(1.2)', cursor: 'pointer' }}
                              />
                            </div>
                            <span className="path-icon" style={{ marginRight: '0.5rem' }}>📄</span>
                            <span className="path-url" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', flex: 1, fontSize: '0.9rem' }}>{path}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                    </div>
                  )}

                </div> {/* End Left Pane */}
                
                {/* Right Pane: Preview */}
                <div className="analysis-preview-pane" style={{ 
                  flex: 1, 
                  background: 'var(--bg-secondary)',
                  padding: '1.5rem',
                  overflowY: 'auto'
                }}>
                  {activePreviewPage ? (
                    <div className="preview-container">
                      <div className="preview-header" style={{ marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
                        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '1.2rem' }}>{activePreviewPage.title || 'Sans titre'}</h3>
                        <a href={activePreviewPage.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'none', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {activePreviewPage.url} <span>↗</span>
                        </a>
                      </div>
                      
                      {activePreviewPage.preview ? (
                        <div className="page-preview-content">
                          {/* Stats Cards */}
                          {activePreviewPage.preview.stats && (
                            <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                               <div className="stat-card" style={{ background: 'var(--card-bg)', padding: '1rem', borderRadius: '8px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                 <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--primary)' }}>{activePreviewPage.preview.stats.total_links || 0}</span>
                                 <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Liens</span>
                               </div>
                               <div className="stat-card" style={{ background: 'var(--card-bg)', padding: '1rem', borderRadius: '8px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                 <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent)' }}>{activePreviewPage.preview.stats.total_images || 0}</span>
                                 <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Images</span>
                               </div>
                               <div className="stat-card" style={{ background: 'var(--card-bg)', padding: '1rem', borderRadius: '8px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                 <span style={{ display: 'block', fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--success)' }}>{activePreviewPage.preview.stats.total_forms || 0}</span>
                                 <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Formulaires</span>
                               </div>
                            </div>
                          )}
                          
                          {/* Meta Info */}
                          {activePreviewPage.preview.meta && (
                            <div className="preview-section" style={{ marginBottom: '2rem' }}>
                              <h4 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-color)' }}>Méta-données</h4>
                              <div style={{ background: 'var(--card-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                {activePreviewPage.preview.meta.description && (
                                  <div style={{ marginBottom: '1rem' }}>
                                    <span style={{ display: 'block', fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Description</span>
                                    <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.5' }}>{activePreviewPage.preview.meta.description}</p>
                                  </div>
                                )}
                                {activePreviewPage.preview.meta['og:image'] && (
                                  <div>
                                    <span style={{ display: 'block', fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Image Sociale</span>
                                    <img src={activePreviewPage.preview.meta['og:image']} alt="OG Image" style={{ maxWidth: '100%', borderRadius: '4px', maxHeight: '200px', objectFit: 'cover' }} />
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {/* Text Preview */}
                          {activePreviewPage.preview.text_preview && (
                            <div className="preview-section" style={{ marginBottom: '2rem' }}>
                              <h4 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-color)' }}>Aperçu du contenu</h4>
                              <div style={{ background: 'var(--card-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.9rem', lineHeight: '1.6', maxHeight: '300px', overflowY: 'auto' }}>
                                {activePreviewPage.preview.text_preview}
                              </div>
                            </div>
                          )}
                          
                          {/* Images Gallery */}
                          {activePreviewPage.preview.images && activePreviewPage.preview.images.length > 0 && (
                            <div className="preview-section">
                              <h4 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--text-color)' }}>Images principales</h4>
                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '1rem' }}>
                                {activePreviewPage.preview.images.slice(0, 8).map((img, i) => (
                                  <div key={i} style={{ position: 'relative', aspectRatio: '1', background: 'var(--card-bg)', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-color)' }}>
                                    <img 
                                      src={img.src} 
                                      alt={img.alt || ''} 
                                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                      loading="lazy"
                                      onError={(e) => e.target.style.display = 'none'}
                                    />
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="empty-preview" style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                          <span style={{ fontSize: '2rem', display: 'block', marginBottom: '1rem' }}>👻</span>
                          <p>Aucune prévisualisation disponible pour cette page.</p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="empty-selection" style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', textAlign: 'center' }}>
                      <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}>👈</div>
                      <h3 style={{ margin: '0 0 0.5rem 0' }}>Sélectionnez une page</h3>
                      <p style={{ margin: 0, maxWidth: '300px' }}>Cliquez sur une page dans la liste de gauche pour voir un aperçu de son contenu.</p>
                    </div>
                  )}
                </div>

              </div> {/* End Split View */}
              
              {/* Detected Content Types */}
              <div className="content-types-section">
                <h3 className="section-title">
                  <span>📦</span>
                  {isBatchMode ? 'Types de contenu à extraire' : 'Types de contenu détectés'}
                </h3>
                
                {contentTypes.length > 0 ? (
                  <div className="content-grid">
                    {contentTypes.map((type) => (
                      <div
                        key={type.id}
                        className={`content-type-card ${selectedTypes.includes(type.id) ? 'selected' : ''}`}
                        onClick={() => toggleContentType(type.id)}
                      >
                        <div className="checkbox-indicator"></div>
                        <span className="material-icons content-icon">{type.icon}</span>
                        <div className="content-title">{type.title}</div>
                        <div className="content-description">{type.description}</div>
                        <div className="content-count">{type.count}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ 
                    padding: '2rem', 
                    textAlign: 'center', 
                    color: 'var(--text-muted)',
                    background: 'var(--card-bg)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)'
                  }}>
                    <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Aucun type de contenu détecté</p>
                    <p style={{ fontSize: '0.9rem' }}>L'analyse n'a trouvé aucun élément extractible sur ce site.</p>
                  </div>
                )}
              </div>
              
              {/* Scrapable Content Details */}
              {scrapableContent && scrapableContent.detected_types && scrapableContent.detected_types.length > 0 && (
                <div className="content-types-section" style={{ marginTop: '2rem' }}>
                  <h3 className="section-title">
                    <span>🔍</span>
                    Contenus scrapables détectés
                  </h3>
                  <div style={{ 
                    marginBottom: '1rem',
                    padding: '0.75rem 1rem',
                    background: 'var(--card-bg)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    fontSize: '0.9rem',
                    color: 'var(--text-muted)'
                  }}>
                    <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                      <span><strong>{scrapableContent.total_types}</strong> types détectés</span>
                      <span>Complexité: <strong>{scrapableContent.structure_complexity}</strong></span>
                      <span>Pagination: <strong>{scrapableContent.has_pagination ? 'Oui' : 'Non'}</strong></span>
                      <span>Recommandation: <strong>{scrapableContent.recommended_action}</strong></span>
                    </div>
                  </div>
                  
                  <div className="content-grid">
                    {scrapableContent.detected_types.map((type, index) => {
                      // Extraire le texte de l'échantillon
                      let sampleText = '';
                      if (type.sample) {
                        if (typeof type.sample === 'string') {
                          sampleText = type.sample;
                        } else if (type.sample.text) {
                          sampleText = type.sample.text;
                        } else if (type.sample.title) {
                          sampleText = type.sample.title;
                        } else if (type.sample.name) {
                          sampleText = type.sample.name;
                        }
                      }
                      
                      // Aperçu par défaut si vide
                      if (!sampleText || sampleText.trim() === '') {
                        if (type.type === 'media') {
                          sampleText = 'Images et médias trouvés sur le site';
                        } else if (type.type === 'tables') {
                          sampleText = 'Tableaux de données structurés';
                        } else if (type.type === 'text_content') {
                          sampleText = 'Contenu textuel principal';
                        } else {
                          sampleText = `Éléments ${type.name} détectés`;
                        }
                      }
                      
                      const isSelected = selectedScrapableTypes.includes(type.type);
                      const isExpanded = expandedScrapable === type.type;
                      
                      return (
                        <div
                          key={`scrapable-${index}`}
                          className={`content-type-card ${isSelected ? 'selected' : ''}`}
                          onClick={() => {
                            if (isSelected) {
                              setSelectedScrapableTypes(prev => prev.filter(t => t !== type.type));
                            } else {
                              setSelectedScrapableTypes(prev => [...prev, type.type]);
                            }
                          }}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className="checkbox-indicator"></div>
                          <span className="material-icons content-icon">{type.icon}</span>
                          <div className="content-title">{type.name}</div>
                          <div className="content-description">{type.description}</div>
                          <div className="content-count" style={{ fontSize: '0.85rem' }}>
                            {type.count || 0} éléments · Confiance: {Math.round(type.confidence * 100)}%
                          </div>
                          <div 
                            onClick={(e) => {
                              e.stopPropagation();
                              setExpandedScrapable(isExpanded ? null : type.type);
                            }}
                            style={{ 
                              marginTop: '0.5rem',
                              padding: '0.5rem',
                              background: 'rgba(255,255,255,0.05)',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              color: 'var(--text-muted)',
                              maxHeight: isExpanded ? '200px' : '60px',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              cursor: 'zoom-in',
                              transition: 'max-height 0.3s ease'
                            }}
                          >
                            <div style={{ marginBottom: '0.25rem', fontWeight: 'bold', fontSize: '0.7rem', opacity: 0.7 }}>
                              Aperçu {isExpanded ? '(cliquer pour réduire)' : '(cliquer pour agrandir)'}
                            </div>
                            {sampleText.substring(0, isExpanded ? 500 : 100)}{sampleText.length > (isExpanded ? 500 : 100) ? '...' : ''}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  {scrapableContent.rejected_types && scrapableContent.rejected_types.length > 0 && (
                    <details style={{ marginTop: '1rem' }}>
                      <summary style={{ 
                        cursor: 'pointer',
                        padding: '0.5rem',
                        fontSize: '0.9rem',
                        color: 'var(--text-muted)'
                      }}>
                        Types rejetés ({scrapableContent.rejected_types.length})
                      </summary>
                      <div style={{ 
                        marginTop: '0.5rem',
                        padding: '1rem',
                        background: 'rgba(255,0,0,0.05)',
                        borderRadius: '6px',
                        fontSize: '0.85rem'
                      }}>
                        {scrapableContent.rejected_types.map((type, idx) => (
                          <div key={idx} style={{ marginBottom: '0.5rem' }}>
                            <strong>{type.name}</strong> - Confiance trop faible ({Math.round(type.confidence * 100)}%)
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              )}
              
              {/* Advanced Options */}
              <div className="advanced-section">
                <button
                  className={`advanced-toggle-btn ${showAdvanced ? 'active' : ''}`}
                  onClick={() => setShowAdvanced(!showAdvanced)}
                >
                  <span>⚙️ Options avancées (pour utilisateurs expérimentés)</span>
                  <span className="toggle-icon">▼</span>
                </button>
                
                <div className={`advanced-content ${showAdvanced ? 'expanded' : ''}`}>
                  <div className="advanced-options-grid">
                    <div className="option-group">
                      <label className="option-label">Profondeur de navigation</label>
                      <select
                        className="option-select"
                        value={advancedOptions.depth}
                        onChange={(e) => setAdvancedOptions({...advancedOptions, depth: e.target.value})}
                      >
                        <option value="1">1 niveau (page actuelle)</option>
                        <option value="2">2 niveaux (pages liées)</option>
                        <option value="3">3 niveaux (navigation profonde)</option>
                        <option value="unlimited">Illimité</option>
                      </select>
                    </div>
                    
                    <div className="option-group">
                      <label className="option-label">Délai entre requêtes (ms)</label>
                      <input
                        type="number"
                        className="option-input"
                        value={advancedOptions.delay}
                        onChange={(e) => setAdvancedOptions({...advancedOptions, delay: e.target.value})}
                        placeholder="500"
                      />
                    </div>
                    
                    <div className="option-group">
                      <label className="option-label">User Agent</label>
                      <select
                        className="option-select"
                        value={advancedOptions.userAgent}
                        onChange={(e) => setAdvancedOptions({...advancedOptions, userAgent: e.target.value})}
                      >
                        <option>Chrome (Desktop)</option>
                        <option>Firefox (Desktop)</option>
                        <option>Safari (Desktop)</option>
                        <option>Mobile (iOS)</option>
                        <option>Mobile (Android)</option>
                      </select>
                    </div>
                    
                    <div className="option-group">
                      <label className="option-label">Timeout (secondes)</label>
                      <input
                        type="number"
                        className="option-input"
                        value={advancedOptions.timeout}
                        onChange={(e) => setAdvancedOptions({...advancedOptions, timeout: e.target.value})}
                        placeholder="30"
                      />
                    </div>
                    <div className="option-group">
                      <label className="option-label">Pages max à scraper</label>
                      <input
                        type="number"
                        className="option-input"
                        value={advancedOptions.max_pages}
                        onChange={(e) => setAdvancedOptions({...advancedOptions, max_pages: e.target.value})}
                        placeholder="Auto"
                      />
                    </div>
                  </div>
                  
                  {/* Custom Selector Input */}
                  <div className="selector-input-section">
                    <div className="selector-title">🎯 Sélecteurs CSS personnalisés (optionnel)</div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                      Pour les utilisateurs avancés : spécifiez vos propres sélecteurs CSS pour extraire des données précises.
                    </p>
                    
                    <div className="selector-fields">
                      {customSelectors.map((selector, index) => (
                        <div key={index} className="selector-field">
                          <input
                            type="text"
                            className="field-input"
                            placeholder="Nom du champ"
                            value={selector.name}
                            onChange={(e) => updateCustomSelector(index, 'name', e.target.value)}
                          />
                          <input
                            type="text"
                            className="field-input"
                            placeholder="Sélecteur CSS"
                            value={selector.selector}
                            onChange={(e) => updateCustomSelector(index, 'selector', e.target.value)}
                          />
                          <button
                            className="btn-remove"
                            onClick={() => removeCustomSelector(index)}
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                    
                    <button className="btn-add-field" onClick={addCustomSelector}>
                      ➕ Ajouter un champ personnalisé
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Storage Format Selection */}
              <div className="storage-section">
                <h3 className="section-title">
                  <span>💾</span>
                  Format de stockage
                </h3>
                <p className="card-description" style={{ marginBottom: '1.5rem' }}>
                  Choisissez le format dans lequel vous souhaitez recevoir vos données extraites.
                </p>
                
                <div className="format-grid">
                  {formats.map((format) => (
                    <div
                      key={format.id}
                      className={`format-card ${selectedFormat === format.id ? 'selected' : ''}`}
                      onClick={() => setSelectedFormat(format.id)}
                    >
                      <div className="format-icon">{format.icon}</div>
                      <div className="format-name">{format.name}</div>
                    </div>
                  ))}
                </div>
                
                {/* Option pour inclure les images en ZIP */}
                <div className="images-zip-option">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={includeImagesZip}
                      onChange={(e) => setIncludeImagesZip(e.target.checked)}
                    />
                    <span className="checkbox-custom"></span>
                    <span className="checkbox-text">
                      🖼️ Inclure les images en ZIP (téléchargement séparé)
                    </span>
                  </label>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="action-buttons">
                <button
                  className="btn-secondary"
                  onClick={() => {
                    setShowResults(false);
                    setCurrentStep(1);
                  }}
                >
                  ← Retour
                </button>
                <button className="btn-primary" onClick={handleStartScraping}>
                  <span>🚀</span>
                  Lancer le scraping
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
