// src/pages/Results/Results.jsx - VERSION CONNECTÉE À L'ANALYSE
import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import Sidebar from '../../components/Sidebar';
import '../../assets/css/dashboard.css';
import '../../assets/css/results.css';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Récupérer les données depuis le state de navigation OU localStorage
  const [scrapingData, setScrapingData] = useState(() => {
    // Essayer de récupérer depuis le state de navigation
    if (location.state?.scrapingData) {
      return generateResultsFromAnalysis(location.state.scrapingData);
    }
    
    // Sinon depuis localStorage
    const saved = localStorage.getItem('scrapingConfig');
    if (saved) {
      return generateResultsFromAnalysis(JSON.parse(saved));
    }
    
    // Données par défaut si rien n'est trouvé
    return getEmptyResults();
  });

  const [exportModal, setExportModal] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState('json');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);

  // Fonction pour générer des résultats BASÉS SUR L'ANALYSE
  function generateResultsFromAnalysis(analysisData) {
    console.log('Génération des résultats depuis:', analysisData);
 if (!analysisData) {
    console.log('Aucune donnée d\'analyse');
    return getEmptyResults();
  }
  
  const { target, selectedElements, config, detectedElements } = analysisData;
  
  console.log('Éléments sélectionnés:', selectedElements);
  console.log('Target:', target);
    
    // if (!analysisData) return getEmptyResults();
    
    // const { target, selectedElements, config, detectedElements } = analysisData;
    
    // // Si aucun élément sélectionné, retourner des résultats vides
    // if (!selectedElements || selectedElements.length === 0) {
    //   return getEmptyResults();
    // }
    
    // Déterminer le type de contenu (utiliser la même logique que dans Analysis)
    const getContentType = () => {
      if (target.type === 'selector') {
        const selector = target.input.toLowerCase();
        if (selector.includes('.product') || selector.includes('.card')) return 'ecommerce';
        if (selector.includes('article') || selector.includes('.post')) return 'blog';
        if (selector.includes('.repo') || selector.includes('.repository')) return 'github';
        if (selector.includes('.template') || selector.includes('.theme')) return 'template';
      }
      
      if (target.type === 'url') {
        const url = target.input.toLowerCase();
        if (url.includes('amazon') || url.includes('ebay') || url.includes('shop')) return 'ecommerce';
        if (url.includes('medium') || url.includes('blog') || url.includes('wordpress')) return 'blog';
        if (url.includes('github')) return 'github';
        if (url.includes('themeforest') || url.includes('template')) return 'template';
      }
      
      return target.type;
    };

    const contentType = getContentType();
    
    // Calculer le nombre total d'éléments basé sur les éléments sélectionnés
    const totalElements = selectedElements.reduce((sum, el) => sum + (el.count || 0), 0);
    
    // Générer des données QUI CORRESPONDENT AUX ÉLÉMENTS SÉLECTIONNÉS
    const data = generateDataForSelectedElements(selectedElements, totalElements, contentType, target);
    
    // Calculer les statistiques BASÉES SUR L'ANALYSE
    const avgConfidence = selectedElements.length > 0 
      ? Math.round(selectedElements.reduce((sum, el) => sum + (el.confidence || 0), 0) / selectedElements.length)
      : 0;
    
    return {
      metadata: {
        projectName: config?.name || 'Scraping sans nom',
        type: target.type,
        url: target.type === 'url' ? target.input : undefined,
        selector: target.type === 'selector' ? target.input : undefined,
        html: target.type === 'html' ? target.input.substring(0, 100) + '...' : undefined,
        contentType: contentType,
        timestamp: new Date().toISOString(),
        elementsScraped: totalElements,
        selectedElements: selectedElements.map(el => ({
          name: el.name,
          count: el.count,
          selector: el.selector,
          confidence: el.confidence,
          icon: el.icon
        })),
        allDetectedElements: detectedElements // Garder trace de tous les éléments détectés
      },
      data: data,
      statistics: {
        totalVolume: calculateTotalVolume(selectedElements),
        successRate: `${avgConfidence}%`,
        avgExtractionTime: calculateExtractionTime(selectedElements, config),
        elementsCount: totalElements,
        lastUpdated: 'À l\'instant'
      }
    };
  }

  // Générer des données SPÉCIFIQUES pour chaque élément sélectionné
  function generateDataForSelectedElements(selectedElements, totalCount, contentType, target) {
    const data = [];
    const itemCount = Math.min(totalCount, 100); // Limiter pour la démo
    
    // Mapper les éléments sélectionnés pour savoir quelles données générer
    const hasProducts = selectedElements.some(el => 
      el.name.toLowerCase().includes('produit') || 
      el.name.toLowerCase().includes('product')
    );
    
    const hasPrices = selectedElements.some(el => 
      el.name.toLowerCase().includes('prix') || 
      el.name.toLowerCase().includes('price')
    );
    
    const hasArticles = selectedElements.some(el => 
      el.name.toLowerCase().includes('article') || 
      el.name.toLowerCase().includes('post')
    );
    
    const hasTitles = selectedElements.some(el => 
      el.name.toLowerCase().includes('titre') || 
      el.name.toLowerCase().includes('title')
    );
    
    const hasAuthors = selectedElements.some(el => 
      el.name.toLowerCase().includes('auteur') || 
      el.name.toLowerCase().includes('author')
    );
    
    const hasImages = selectedElements.some(el => 
      el.name.toLowerCase().includes('image') || 
      el.name.toLowerCase().includes('img')
    );
    
    const hasReviews = selectedElements.some(el => 
      el.name.toLowerCase().includes('avis') || 
      el.name.toLowerCase().includes('review') ||
      el.name.toLowerCase().includes('rating')
    );
    
    const hasCategories = selectedElements.some(el => 
      el.name.toLowerCase().includes('catégorie') || 
      el.name.toLowerCase().includes('category')
    );
    
    const hasRepositories = selectedElements.some(el => 
      el.name.toLowerCase().includes('repository') || 
      el.name.toLowerCase().includes('repo')
    );
    
    const hasStars = selectedElements.some(el => 
      el.name.toLowerCase().includes('star') || 
      el.name.toLowerCase().includes('étoile')
    );
    
    const hasTemplates = selectedElements.some(el => 
      el.name.toLowerCase().includes('template') || 
      el.name.toLowerCase().includes('theme')
    );

    // Générer les données selon le type de contenu ET les éléments sélectionnés
    for (let i = 1; i <= itemCount; i++) {
      const item = { id: i };
      
      if (contentType === 'ecommerce' || hasProducts) {
        if (hasProducts) {
          item.name = `Produit ${i} - ${getRandomProductName()}`;
        }
        
        if (hasPrices) {
          item.price = `${getRandomPrice()}€`;
          if (Math.random() > 0.7) {
            item.originalPrice = `${(parseFloat(item.price) * 1.2).toFixed(2)}€`;
            item.discount = `${Math.floor(Math.random() * 30)}%`;
          }
        }
        
        if (hasImages) {
          item.image = `product-image-${i}.jpg`;
          item.imageCount = Math.floor(Math.random() * 5) + 1;
        }
        
        if (hasReviews) {
          item.rating = (Math.random() * 2 + 3).toFixed(1);
          item.reviewCount = Math.floor(Math.random() * 500);
        }
        
        if (hasCategories) {
          item.category = getRandomCategory();
          item.subcategory = getRandomSubcategory(item.category);
        }
        
        item.stock = getRandomStockStatus();
        item.date = getRandomRecentDate();
        item.type = 'product';
      }
      
      else if (contentType === 'blog' || hasArticles) {
        if (hasTitles || hasArticles) {
          item.title = `${getRandomArticleTitle()} ${i}`;
        }
        
        if (hasArticles) {
          item.excerpt = `Extrait de l'article ${i}. Ceci est un contenu intéressant sur ${getRandomTopic()}...`;
          item.contentLength = `${Math.floor(Math.random() * 2000) + 500} mots`;
        }
        
        if (hasAuthors) {
          item.author = getRandomAuthor();
          item.authorBio = `Auteur spécialisé en ${getRandomTopic()}`;
        }
        
        if (hasCategories) {
          item.category = getRandomBlogCategory();
          item.tags = getRandomTags(3);
        }
        
        item.date = getRandomRecentDate();
        item.views = Math.floor(Math.random() * 10000);
        item.readTime = `${Math.ceil(Math.random() * 20)} min`;
        item.type = 'article';
      }
      
      else if (contentType === 'github' || hasRepositories) {
        if (hasRepositories || hasTitles) {
          item.repository = `${getRandomTech()}-project-${i}`;
          item.description = `Repository ${i}: ${getRandomDescription()}`;
        }
        
        if (hasStars) {
          item.stars = Math.floor(Math.random() * 10000);
          item.starTrend = Math.random() > 0.5 ? 'up' : 'down';
        }
        
        item.forks = Math.floor(Math.random() * 500);
        item.language = getRandomLanguage();
        item.lastCommit = getRandomRecentDate();
        item.issues = Math.floor(Math.random() * 50);
        item.topics = getRandomTopics(4);
        item.type = 'repository';
      }
      
      else if (contentType === 'template' || hasTemplates) {
        if (hasTemplates || hasTitles) {
          item.templateName = `${getRandomTemplateType()} Template ${i}`;
          item.description = `Template professionnel pour ${getRandomTemplatePurpose()}`;
        }
        
        if (hasPrices) {
          item.price = `${getRandomTemplatePrice()}$`;
          item.license = getRandomLicense();
        }
        
        if (hasCategories) {
          item.category = getRandomTemplateCategory();
          item.framework = getRandomFramework();
        }
        
        item.sales = Math.floor(Math.random() * 1000);
        item.rating = (Math.random() * 2 + 3).toFixed(1);
        item.lastUpdate = getRandomRecentDate();
        item.features = getRandomFeatures(5);
        item.type = 'template';
      }
      
      else {
        // Données génériques basées sur les éléments sélectionnés
        selectedElements.forEach((element, index) => {
          const key = element.name.toLowerCase().replace(/\s+/g, '_');
          item[key] = `Donnée ${i} pour ${element.name}`;
          
          if (element.selector) {
            item[`${key}_selector`] = element.selector;
          }
          
          if (element.count) {
            item[`${key}_count`] = element.count;
          }
        });
        
        item.type = 'generic';
        item.date = getRandomRecentDate();
      }
      
      data.push(item);
    }
    
    return data;
  }

  // Fonctions utilitaires pour générer des données réalistes
  function getRandomProductName() {
    const products = ['iPhone', 'Samsung Galaxy', 'Google Pixel', 'MacBook Pro', 'iPad', 'AirPods', 'PlayStation', 'Xbox', 'Nintendo Switch'];
    const adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Elite', 'Standard', 'Lite', 'Edition'];
    return `${products[Math.floor(Math.random() * products.length)]} ${adjectives[Math.floor(Math.random() * adjectives.length)]}`;
  }

  function getRandomPrice() {
    const prices = [99.99, 129.99, 199.99, 249.99, 299.99, 399.99, 499.99, 799.99, 999.99, 1299.99];
    return prices[Math.floor(Math.random() * prices.length)];
  }

  function getRandomCategory() {
    const categories = ['Électronique', 'Mode', 'Maison', 'Sport', 'Jeux', 'Livres', 'Beauté', 'Santé'];
    return categories[Math.floor(Math.random() * categories.length)];
  }

  function getRandomSubcategory(category) {
    const subcategories = {
      'Électronique': ['Smartphones', 'Ordinateurs', 'Audio', 'Photographie'],
      'Mode': ['Vêtements', 'Chaussures', 'Accessoires', 'Montres'],
      'Maison': ['Meubles', 'Décoration', 'Cuisine', 'Jardin'],
      'Sport': ['Fitness', 'Running', 'Yoga', 'Cyclisme']
    };
    return subcategories[category] ? subcategories[category][Math.floor(Math.random() * subcategories[category].length)] : 'Autre';
  }

  function getRandomStockStatus() {
    const statuses = ['in-stock', 'low-stock', 'out-of-stock', 'pre-order'];
    return statuses[Math.floor(Math.random() * statuses.length)];
  }

  function getRandomArticleTitle() {
    const prefixes = ['Guide complet', 'Tutoriel', 'Nouvelle', 'Analyse', 'Revue', 'Comparaison', 'Tips & Tricks'];
    const topics = ['React', 'Vue.js', 'Node.js', 'TypeScript', 'Python', 'Machine Learning', 'Web Design', 'SEO'];
    return `${prefixes[Math.floor(Math.random() * prefixes.length)]} sur ${topics[Math.floor(Math.random() * topics.length)]}`;
  }

  function getRandomTopic() {
    const topics = ['React', 'JavaScript', 'Python', 'AI', 'Web Development', 'Design', 'Marketing', 'Productivity'];
    return topics[Math.floor(Math.random() * topics.length)];
  }

  function getRandomAuthor() {
    const authors = ['Jean Dupont', 'Marie Martin', 'Alexandre Bernard', 'Sophie Lambert', 'Thomas Petit', 'Camille Robert'];
    return authors[Math.floor(Math.random() * authors.length)];
  }

  function getRandomBlogCategory() {
    const categories = ['Technologie', 'Design', 'Business', 'Lifestyle', 'Productivité', 'Éducation'];
    return categories[Math.floor(Math.random() * categories.length)];
  }

  function getRandomTags(count) {
    const tags = ['web', 'frontend', 'backend', 'fullstack', 'javascript', 'react', 'vue', 'node', 'python', 'ai'];
    return tags.sort(() => 0.5 - Math.random()).slice(0, count);
  }

  function getRandomTech() {
    const techs = ['react', 'vue', 'nextjs', 'nuxt', 'angular', 'svelte', 'typescript', 'python'];
    return techs[Math.floor(Math.random() * techs.length)];
  }

  function getRandomDescription() {
    const descs = ['Framework moderne', 'Library puissante', 'Tool pratique', 'Template utile', 'Projet open-source'];
    return descs[Math.floor(Math.random() * descs.length)];
  }

  function getRandomLanguage() {
    const langs = ['JavaScript', 'TypeScript', 'Python', 'Go', 'Rust', 'Java', 'C++', 'PHP'];
    return langs[Math.floor(Math.random() * langs.length)];
  }

  function getRandomTopics(count) {
    const topics = ['web', 'frontend', 'backend', 'fullstack', 'api', 'database', 'security', 'performance'];
    return topics.sort(() => 0.5 - Math.random()).slice(0, count);
  }

  function getRandomTemplateType() {
    const types = ['Business', 'Creative', 'Portfolio', 'E-commerce', 'Corporate', 'Minimal', 'Modern'];
    return types[Math.floor(Math.random() * types.length)];
  }

  function getRandomTemplatePurpose() {
    const purposes = ['site vitrine', 'blog professionnel', 'boutique en ligne', 'portfolio créatif', 'landing page'];
    return purposes[Math.floor(Math.random() * purposes.length)];
  }

  function getRandomTemplatePrice() {
    const prices = [29, 49, 79, 99, 149, 199];
    return prices[Math.floor(Math.random() * prices.length)];
  }

  function getRandomLicense() {
    const licenses = ['Licence Standard', 'Licence Étendue', 'Licence Développeur'];
    return licenses[Math.floor(Math.random() * licenses.length)];
  }

  function getRandomTemplateCategory() {
    const categories = ['HTML', 'WordPress', 'React', 'Vue', 'Shopify', 'Webflow'];
    return categories[Math.floor(Math.random() * categories.length)];
  }

  function getRandomFramework() {
    const frameworks = ['Bootstrap', 'Tailwind', 'Material-UI', 'Bulma', 'Foundation'];
    return frameworks[Math.floor(Math.random() * frameworks.length)];
  }

  function getRandomFeatures(count) {
    const features = ['Responsive', 'SEO Friendly', 'Customizable', 'Well Documented', 'Fast Loading', 'Cross Browser', 'Retina Ready'];
    return features.sort(() => 0.5 - Math.random()).slice(0, count);
  }

  function getRandomRecentDate() {
    const now = new Date();
    const randomHours = Math.floor(Math.random() * 168); // Jusqu'à 7 jours dans le passé
    const date = new Date(now.getTime() - randomHours * 3600000);
    
    return date.toLocaleString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function calculateTotalVolume(selectedElements) {
    const totalElements = selectedElements.reduce((sum, el) => sum + (el.count || 0), 0);
    const avgBytesPerElement = 200; // Estimation moyenne
    const totalBytes = totalElements * avgBytesPerElement;
    return `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function calculateExtractionTime(selectedElements, config) {
    const totalElements = selectedElements.reduce((sum, el) => sum + (el.count || 0), 0);
    const delay = config?.delay || 'normal';
    const delayMs = {
      'fast': 100,
      'normal': 500,
      'slow': 1000,
      'very-slow': 2000
    }[delay] || 500;
    
    const totalTime = (totalElements * delayMs) / 1000;
    return `${(totalTime / 60).toFixed(1)} min`;
  }

  function getEmptyResults() {
    return {
      metadata: {
        projectName: 'Aucun scraping en cours',
        type: 'none',
        selectedElements: [],
        elementsScraped: 0
      },
      data: [],
      statistics: {
        totalVolume: '0 MB',
        successRate: '0%',
        avgExtractionTime: '0s',
        elementsCount: 0,
        lastUpdated: 'Jamais'
      }
    };
  }

  // Charger les données au montage
//   useEffect(() => {
//     const savedConfig = localStorage.getItem('scrapingConfig');
//     if (savedConfig) {
//       try {
//         const analysisData = JSON.parse(savedConfig);
//         setScrapingData(generateResultsFromAnalysis(analysisData));
//       } catch (error) {
//         console.error('Erreur de parsing de la configuration:', error);
//       }
//     }
//   }, []);
useEffect(() => {
  // D'abord essayer depuis le state de navigation
  if (location.state?.scrapingData) {
    console.log('Données reçues depuis le state:', location.state.scrapingData);
    const results = generateResultsFromAnalysis(location.state.scrapingData);
    setScrapingData(results);
    
    // Sauvegarder aussi dans localStorage pour persistance
    localStorage.setItem('scrapingConfig', JSON.stringify(location.state.scrapingData));
    return;
  }
  
  // Sinon depuis localStorage
  const savedConfig = localStorage.getItem('scrapingConfig');
  if (savedConfig) {
    console.log('Données chargées depuis localStorage:', savedConfig);
    try {
      const analysisData = JSON.parse(savedConfig);
      const results = generateResultsFromAnalysis(analysisData);
      setScrapingData(results);
    } catch (error) {
      console.error('Erreur de parsing de la configuration:', error);
    }
  } else {
    console.log('Aucune configuration trouvée');
    setScrapingData(getEmptyResults());
  }
}, [location.state]); 

  // Rendu des colonnes BASÉ SUR LES ÉLÉMENTS SÉLECTIONNÉS
  const renderTableHeaders = () => {
    const { selectedElements, contentType } = scrapingData.metadata;
    
    if (selectedElements.length === 0) {
      return (
        <>
          <th>AUCUN ÉLÉMENT</th>
          <th>SÉLECTIONNÉ</th>
        </>
      );
    }
    
    // Afficher les colonnes selon les éléments sélectionnés
    const headers = [];
    
    selectedElements.forEach(element => {
      const elementName = element.name.toLowerCase();
      
      if (elementName.includes('produit') || elementName.includes('product') || 
          elementName.includes('template') || elementName.includes('repository')) {
        headers.push(
          <th key={`header-${element.name}`} onClick={() => handleSort('name')}>
            {element.name.toUpperCase()}
            {sortConfig.key === 'name' && (
              <i className={`fas fa-arrow-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
            )}
          </th>
        );
      }
      
      if (elementName.includes('prix') || elementName.includes('price')) {
        headers.push(
          <th key={`header-price`} onClick={() => handleSort('price')}>
            PRIX
            {sortConfig.key === 'price' && (
              <i className={`fas fa-arrow-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
            )}
          </th>
        );
      }
      
      if (elementName.includes('titre') || elementName.includes('title')) {
        headers.push(<th key={`header-title`}>TITRE</th>);
      }
      
      if (elementName.includes('auteur') || elementName.includes('author')) {
        headers.push(<th key={`header-author`}>AUTEUR</th>);
      }
      
      if (elementName.includes('image') || elementName.includes('img')) {
        headers.push(<th key={`header-image`}>IMAGES</th>);
      }
      
      if (elementName.includes('avis') || elementName.includes('review') || elementName.includes('rating')) {
        headers.push(<th key={`header-rating`}>NOTATION</th>);
      }
      
      if (elementName.includes('catégorie') || elementName.includes('category')) {
        headers.push(<th key={`header-category`}>CATÉGORIE</th>);
      }
      
      if (elementName.includes('star') || elementName.includes('étoile')) {
        headers.push(
          <th key={`header-stars`} onClick={() => handleSort('stars')}>
            STARS
            {sortConfig.key === 'stars' && (
              <i className={`fas fa-arrow-${sortConfig.direction === 'asc' ? 'up' : 'down'}`}></i>
            )}
          </th>
        );
      }
      
      if (elementName.includes('language') || elementName.includes('langage')) {
        headers.push(<th key={`header-language`}>LANGAGE</th>);
      }
    });
    
    // Colonnes communes
    headers.push(<th key="header-date">DATE EXTRACTION</th>);
    headers.push(<th key="header-actions">ACTIONS</th>);
    
    return headers;
  };

  // Rendu des lignes BASÉ SUR LES DONNÉES GÉNÉRÉES
  const renderTableRow = (item) => {
    const { selectedElements } = scrapingData.metadata;
    
    return (
      <tr key={item.id}>
        {selectedElements.map(element => {
          const elementName = element.name.toLowerCase();
          
          if (elementName.includes('produit') || elementName.includes('product')) {
            return (
              <td key={`cell-${element.name}-${item.id}`}>
                <div className="product-info">
                  <div className="product-image-placeholder">
                    <i className={element.icon || "fas fa-box"}></i>
                  </div>
                  <div>
                    <strong>{item.name || `Produit ${item.id}`}</strong>
                    {item.description && <p className="product-description">{item.description}</p>}
                  </div>
                </div>
              </td>
            );
          }
          
          if (elementName.includes('prix') || elementName.includes('price')) {
            return (
              <td key={`cell-price-${item.id}`}>
                <span className="product-price">{item.price || 'N/A'}</span>
                {item.discount && (
                  <span className="price-change negative">-{item.discount}</span>
                )}
                {item.originalPrice && (
                  <div className="original-price">{item.originalPrice}</div>
                )}
              </td>
            );
          }
          
          if (elementName.includes('titre') || elementName.includes('title')) {
            return (
              <td key={`cell-title-${item.id}`}>
                <strong>{item.title || `Titre ${item.id}`}</strong>
                {item.excerpt && <p className="article-excerpt">{item.excerpt}</p>}
              </td>
            );
          }
          
          if (elementName.includes('auteur') || elementName.includes('author')) {
            return (
              <td key={`cell-author-${item.id}`}>
                <div className="author-info">
                  <i className="fas fa-user"></i>
                  <span>{item.author || 'Auteur inconnu'}</span>
                </div>
              </td>
            );
          }
          
          if (elementName.includes('image') || elementName.includes('img')) {
            return (
              <td key={`cell-image-${item.id}`}>
                <div className="image-info">
                  <i className="fas fa-image"></i>
                  <span>{item.imageCount || 1} image(s)</span>
                </div>
              </td>
            );
          }
          
          if (elementName.includes('avis') || elementName.includes('review') || elementName.includes('rating')) {
            return (
              <td key={`cell-rating-${item.id}`}>
                <div className="rating-info">
                  <div className="stars">
                    {'★'.repeat(Math.floor(item.rating || 0))}
                    {'☆'.repeat(5 - Math.floor(item.rating || 0))}
                  </div>
                  <span>{item.rating || '0.0'}/5</span>
                  {item.reviewCount && <small>({item.reviewCount} avis)</small>}
                </div>
              </td>
            );
          }
          
          if (elementName.includes('catégorie') || elementName.includes('category')) {
            return (
              <td key={`cell-category-${item.id}`}>
                <span className="category-badge">{item.category || 'Non catégorisé'}</span>
                {item.subcategory && <small>{item.subcategory}</small>}
              </td>
            );
          }
          
          if (elementName.includes('stock') || elementName.includes('in-stock')) {
            return (
              <td key={`cell-stock-${item.id}`}>
                <span className={`stock-status ${item.stock || 'unknown'}`}>
                  {item.stock === 'in-stock' ? 'En Stock' : 
                   item.stock === 'low-stock' ? 'Stock Faible' : 
                   item.stock === 'out-of-stock' ? 'Rupture' : 
                   'Inconnu'}
                </span>
              </td>
            );
          }
          
          if (elementName.includes('star') || elementName.includes('étoile')) {
            return (
              <td key={`cell-stars-${item.id}`}>
                <span className="stars-count">
                  <i className="fas fa-star"></i>
                  {item.stars ? item.stars.toLocaleString() : '0'}
                </span>
              </td>
            );
          }
          
          if (elementName.includes('language') || elementName.includes('langage')) {
            return (
              <td key={`cell-language-${item.id}`}>
                <span className="language-badge">{item.language || 'Inconnu'}</span>
              </td>
            );
          }
          
          if (elementName.includes('template')) {
            return (
              <td key={`cell-template-${item.id}`}>
                <strong>{item.templateName || `Template ${item.id}`}</strong>
                {item.description && <p className="template-description">{item.description}</p>}
              </td>
            );
          }
          
          if (elementName.includes('repository') || elementName.includes('repo')) {
            return (
              <td key={`cell-repo-${item.id}`}>
                <div className="repo-info">
                  <i className="fab fa-github"></i>
                  <div>
                    <strong>{item.repository || `repo-${item.id}`}</strong>
                    {item.description && <p className="repo-description">{item.description}</p>}
                  </div>
                </div>
              </td>
            );
          }
          
          // Pour les éléments génériques
          return (
            <td key={`cell-generic-${element.name}-${item.id}`}>
              {item[element.name.toLowerCase().replace(/\s+/g, '_')] || `Donnée ${item.id}`}
            </td>
          );
        })}
        
        <td>{item.date || new Date().toLocaleString('fr-FR')}</td>
        <td className="actions-cell">
          <button className="action-btn" title="Voir les détails" onClick={() => viewDetails(item)}>
            <i className="fas fa-eye"></i>
          </button>
          <button className="action-btn" title="Exporter" onClick={() => exportItem(item)}>
            <i className="fas fa-download"></i>
          </button>
          <button className="action-btn" title="Plus d'options">
            <i className="fas fa-ellipsis-v"></i>
          </button>
        </td>
      </tr>
    );
  };

  // Filtrage et tri
  const filteredData = scrapingData.data.filter(item => {
    if (!searchTerm) return true;
    
    const searchable = Object.values(item).join(' ').toLowerCase();
    return searchable.includes(searchTerm.toLowerCase());
  });

  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortConfig.key) return 0;
    
    let aVal = a[sortConfig.key];
    let bVal = b[sortConfig.key];
    
    if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const totalPages = Math.ceil(sortedData.length / rowsPerPage);
  const paginatedData = sortedData.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const viewDetails = (item) => {
    console.log('View details:', item);
    alert(`Détails de l'élément #${item.id}\n\n${JSON.stringify(item, null, 2)}`);
  };

  const exportItem = (item) => {
    const blob = new Blob([JSON.stringify(item, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `element-${item.id}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportToFormat = (format) => {
    let content, mimeType, extension;
    
    switch(format.toLowerCase()) {
      case 'csv':
        content = convertToCSV(scrapingData);
        mimeType = 'text/csv';
        extension = 'csv';
        break;
      case 'json':
      default:
        content = JSON.stringify(scrapingData, null, 2);
        mimeType = 'application/json';
        extension = 'json';
        break;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scraping-results-${Date.now()}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setExportModal(false);
  };

  const convertToCSV = (data) => {
    if (!data.data || data.data.length === 0) return '';
    
    const headers = Object.keys(data.data[0]).join(',');
    const rows = data.data.map(item => 
      Object.values(item).map(val => 
        typeof val === 'object' ? JSON.stringify(val).replace(/"/g, '""') : 
        val ? String(val).replace(/"/g, '""') : ''
      ).join(',')
    );
    
    return [headers, ...rows].join('\n');
  };

  return (
    <div className="dashboard-container">
      <Sidebar />

      <main className="main-content">
        <header className="top-bar">
          {/* <div className="breadcrumb">
            <Link to="/tasks">Tâches</Link> / 
            <Link to="/analysis">Configuration</Link> / 
            <span>{scrapingData.metadata.projectName}</span>
          </div> */}
          <div className="breadcrumb">
          <Link to="/dashboard">Tableau de Bord</Link> / 
          <Link to="/analysis">Analyse</Link> / 
          <span>
            {scrapingData.metadata.projectName || 'Chargement...'}
            <small style={{ marginLeft: '10px', color: '#666' }}>
              ({scrapingData.metadata.selectedElements?.length || 0} éléments)
            </small>
          </span>
        </div>
          <div className="top-bar-actions">
            <Link to="/analysis" className="btn btn-primary">
              <i className="fas fa-chart-line"></i>
              Voir l'Analyse
            </Link>
            <button className="btn btn-secondary" onClick={() => setExportModal(true)}>
              <i className="fas fa-file-export"></i>
              Exporter
            </button>
          </div>
        </header>

        <div className="results-container">
          <div className="results-header">
            <h2>
              <i className="fas fa-database"></i> 
              Résultats de Scraping: {scrapingData.metadata.projectName}
            </h2>
            <p>
              {scrapingData.statistics.elementsCount.toLocaleString()} éléments extraits
              {scrapingData.metadata.url && ` depuis ${scrapingData.metadata.url}`}
              {scrapingData.metadata.selector && ` avec le sélecteur ${scrapingData.metadata.selector}`}
            </p>
            
            <div className="selected-elements-summary">
              <h4>Éléments sélectionnés :</h4>
              <div className="elements-tags">
                {scrapingData.metadata.selectedElements.map((element, index) => (
                  <span key={index} className="element-tag">
                    <i className={element.icon || "fas fa-check"}></i>
                    {element.name} ({element.count} éléments)
                    <span className="confidence-badge">{element.confidence}%</span>
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="results-controls">
            <div className="search-box">
              <i className="fas fa-search"></i>
              <input 
                type="text" 
                placeholder="Rechercher dans les résultats..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="control-buttons">
              <button className="btn btn-secondary">
                <i className="fas fa-filter"></i>
                Filtrer
              </button>
              <button className="btn btn-secondary" onClick={() => window.location.reload()}>
                <i className="fas fa-sync"></i>
                Actualiser
              </button>
            </div>
          </div>

          <div className="results-stats">
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-database"></i>
              </div>
              <div className="stat-info">
                <h4>Volume total</h4>
                <p className="stat-number">{scrapingData.statistics.totalVolume}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-check-circle"></i>
              </div>
              <div className="stat-info">
                <h4>Taux de réussite</h4>
                <p className="stat-number">{scrapingData.statistics.successRate}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-clock"></i>
              </div>
              <div className="stat-info">
                <h4>Temps d'extraction</h4>
                <p className="stat-number">{scrapingData.statistics.avgExtractionTime}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-box"></i>
              </div>
              <div className="stat-info">
                <h4>Éléments extraits</h4>
                <p className="stat-number">{scrapingData.statistics.elementsCount.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="results-table-container">
            <table className="results-table">
              <thead>
                <tr>
                  {renderTableHeaders()}
                </tr>
              </thead>
              <tbody>
                {paginatedData.map(item => renderTableRow(item))}
              </tbody>
            </table>

            {paginatedData.length === 0 && (
              <div className="no-results">
                <i className="fas fa-search"></i>
                <h3>Aucun résultat trouvé</h3>
                <p>
                  {scrapingData.metadata.selectedElements.length === 0 
                    ? 'Commencez par analyser et sélectionner des éléments à scraper.' 
                    : 'Essayez de modifier vos critères de recherche.'}
                </p>
                {scrapingData.metadata.selectedElements.length === 0 && (
                  <Link to="/analysis" className="btn btn-primary">
                    <i className="fas fa-arrow-right"></i>
                    Aller à l'Analyse
                  </Link>
                )}
              </div>
            )}

            {paginatedData.length > 0 && (
              <div className="pagination">
                <div className="rows-per-page">
                  <span>Lignes par page:</span>
                  <select 
                    value={rowsPerPage} 
                    onChange={(e) => setRowsPerPage(Number(e.target.value))}
                  >
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>

                <div className="page-numbers">
                  <button 
                    className="page-btn" 
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                  >
                    <i className="fas fa-chevron-left"></i>
                  </button>
                  
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (currentPage <= 3) {
                      pageNum = i + 1;
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = currentPage - 2 + i;
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        className={`page-btn ${currentPage === pageNum ? 'active' : ''}`}
                        onClick={() => setCurrentPage(pageNum)}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                  
                  {totalPages > 5 && currentPage < totalPages - 2 && (
                    <>
                      <span>...</span>
                      <button 
                        className="page-btn"
                        onClick={() => setCurrentPage(totalPages)}
                      >
                        {totalPages}
                      </button>
                    </>
                  )}
                  
                  <button 
                    className="page-btn" 
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <i className="fas fa-chevron-right"></i>
                  </button>
                </div>
                
                <div className="pagination-info">
                  Affichage de {(currentPage - 1) * rowsPerPage + 1} à {Math.min(currentPage * rowsPerPage, sortedData.length)} sur {sortedData.length} éléments
                </div>
              </div>
            )}
          </div>

          <div className="export-options-card">
            <h3><i className="fas fa-file-export"></i> Options d'Export</h3>
            <p>Sélectionnez les formats pour exporter vos données scrappées.</p>

            <div className="export-buttons">
              <button className="export-btn" onClick={() => exportToFormat('CSV')}>
                <i className="fas fa-file-csv"></i>
                CSV
              </button>
              <button className="export-btn" onClick={() => exportToFormat('JSON')}>
                <i className="fas fa-file-code"></i>
                JSON
              </button>
              <button className="export-btn" onClick={() => exportToFormat('Excel')}>
                <i className="fas fa-file-excel"></i>
                Excel
              </button>
            </div>
          </div>
        </div>
      </main>

      {exportModal && (
        <div className="modal-overlay" onClick={() => setExportModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3><i className="fas fa-file-export"></i> Exporter les données</h3>
              <button className="modal-close" onClick={() => setExportModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Exportez {scrapingData.data.length} éléments au format :</p>
              
              <div className="export-format-options">
                <label className="format-option">
                  <input 
                    type="radio" 
                    name="exportFormat" 
                    value="json" 
                    checked={selectedFormat === 'json'}
                    onChange={(e) => setSelectedFormat(e.target.value)}
                  />
                  <div className="format-content">
                    <i className="fas fa-file-code"></i>
                    <div>
                      <strong>JSON</strong>
                      <small>Structure hiérarchique complète</small>
                    </div>
                  </div>
                </label>
                
                <label className="format-option">
                  <input 
                    type="radio" 
                    name="exportFormat" 
                    value="csv" 
                    checked={selectedFormat === 'csv'}
                    onChange={(e) => setSelectedFormat(e.target.value)}
                  />
                  <div className="format-content">
                    <i className="fas fa-file-csv"></i>
                    <div>
                      <strong>CSV</strong>
                      <small>Tableur compatible Excel</small>
                    </div>
                  </div>
                </label>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setExportModal(false)}>
                Annuler
              </button>
              <button className="btn btn-primary" onClick={() => exportToFormat(selectedFormat)}>
                <i className="fas fa-download"></i>
                Télécharger
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;