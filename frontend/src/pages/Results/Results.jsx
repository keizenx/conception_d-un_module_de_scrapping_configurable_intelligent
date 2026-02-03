// C:\Users\Admin\Downloads\scrapping.web\scrapping.web\scraper-pro\frontend\src\pages\Results\Results.jsx
// Page d'affichage des résultats de scraping avec tableau de données, filtres et export
// Cette page permet de visualiser et gérer les données extraites d'une session de scraping
// RELEVANT FILES: frontend/src/assets/css/results.css, frontend/src/App.jsx, backend/src/api/routes/export.py

import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import api from '../../services/api';
import '../../assets/css/results.css';

// Mapping des catégories vers des noms et icônes français
const CATEGORY_CONFIG = {
  main_headings: { icon: '📌', name: 'Titres Principaux', color: '#FF4D00' },
  section_headings: { icon: '📑', name: 'Titres de Section', color: '#00E5FF' },
  sub_headings: { icon: '📎', name: 'Sous-titres', color: '#00FF88' },
  paragraphs: { icon: '📝', name: 'Paragraphes', color: '#FFB800' },
  links: { icon: '🔗', name: 'Liens', color: '#9D4EDD' },
  buttons: { icon: '🔘', name: 'Boutons', color: '#FF6B6B' },
  lists: { icon: '📋', name: 'Listes', color: '#4ECDC4' },
  navigation: { icon: '🧭', name: 'Navigation', color: '#45B7D1' },
  footer: { icon: '📄', name: 'Pied de page', color: '#6C757D' },
  code: { icon: '💻', name: 'Code', color: '#20C997' },
  other: { icon: '📦', name: 'Autres contenus', color: '#ADB5BD' },
  images: { icon: '🖼️', name: 'Images', color: '#E91E63' },
  image: { icon: '🖼️', name: 'Images', color: '#E91E63' },
  videos: { icon: '🎬', name: 'Vidéos', color: '#FF5722' },
  video: { icon: '🎬', name: 'Vidéos', color: '#FF5722' },
  audios: { icon: '🎵', name: 'Audio', color: '#9C27B0' },
  documents: { icon: '📑', name: 'Documents', color: '#607D8B' },
  text: { icon: '📝', name: 'Texte', color: '#FFB800' }
};

// Helper pour obtenir la config d'une catégorie
const getCategoryConfig = (category) => {
  const key = category?.toLowerCase().replace(/[\s-]/g, '_');
  return CATEGORY_CONFIG[key] || { icon: '📦', name: category || 'Contenu', color: '#ADB5BD' };
};

function Results() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  
  // State pour les données de l'API
  const [sessionId, setSessionId] = useState(null);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State pour la sélection des éléments
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [selectAll, setSelectAll] = useState(false);
  
  // State pour la prévisualisation
  const [previewItem, setPreviewItem] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  
  // State pour le format d'export pré-sélectionné (depuis la page Analysis)
  const [preSelectedFormat, setPreSelectedFormat] = useState(null);
  const [includeImagesZip, setIncludeImagesZip] = useState(false);
  const [showExportPrompt, setShowExportPrompt] = useState(false);
  const exportTriggered = useRef(false);
  
  // State pour l'export en cours (loading)
  const [exportingFormat, setExportingFormat] = useState(null);
  
  // State pour le modal de sélection d'export
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportModalFormat, setExportModalFormat] = useState(null);
  const [exportLimit, setExportLimit] = useState(100);
  const [exportSelectedOnly, setExportSelectedOnly] = useState(false);
  
  // Récupérer l'ID de session et le format d'export depuis l'URL
  useEffect(() => {
    const loadSessionId = async () => {
      const sessionFromParams = searchParams.get('session');
      const formatFromParams = searchParams.get('format');
      const imagesZipFromParams = searchParams.get('images_zip');
      const sessionFromState = location.state?.sessionId;
      const formatFromState = location.state?.exportFormat;
      const imagesZipFromState = location.state?.includeImagesZip;
      
      let id = sessionFromParams || sessionFromState;
      const format = formatFromParams || formatFromState;
      const imagesZip = imagesZipFromParams === 'true' || imagesZipFromState;
      
      // Si pas de session dans l'URL, essayer de charger la dernière session de l'utilisateur
      if (!id) {
        try {
          const latestSession = await api.getLatestSession();
          if (latestSession && latestSession.session_id) {
            id = latestSession.session_id;
            console.log('[Results] Dernière session chargée:', id);
          }
        } catch (err) {
          console.log('[Results] Pas de session récente trouvée:', err.message);
        }
      }
      
      if (id) {
        setSessionId(id);
      } else {
        setIsLoading(false);
      }
      
      // Stocker le format pré-sélectionné
      if (format && format !== 'none') {
        setPreSelectedFormat(format);
      }
      
      // Stocker l'option images ZIP
      if (imagesZip) {
        setIncludeImagesZip(true);
      }
    };
    
    loadSessionId();
  }, [searchParams, location]);
  
  // Charger les résultats depuis l'API
  useEffect(() => {
    const loadResults = async () => {
      if (!sessionId) {
        setIsLoading(false);
        return;
      }
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Charger les résultats avec filtres
        const filters = {
          search: searchTerm,
          status: activeFilter === 'all' ? null : activeFilter
        };
        
        const data = await api.getResults(sessionId, filters);
        
        // Mettre à jour les infos de session depuis la structure réelle de l'API
        setSessionInfo({
          status: data.status || 'completed',
          date: data.metadata?.created_at ? new Date(data.metadata.created_at).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR'),
          items: data.statistics?.total_items || 0,
          url: data.url || ''
        });
        
        // Transformer scraped_data vers le format attendu par le tableau
        // Supporte maintenant les données GROUPÉES
        const transformedResults = (data.scraped_data || []).map((item, index) => {
          const titre = item.titre || item.title || '';
          const isGrouped = item.elements && Array.isArray(item.elements);
          const type = item.type_contenu || item.type_media || item.category || 'text';
          
          // Pour les médias groupés
          const isMediaGroup = item.type_media && isGrouped;
          const isImage = type === 'image' || item.categorie === 'images';
          const isVideo = type === 'video' || item.categorie === 'videos';
          const isLink = type === 'link' || item.categorie === 'links';
          
          // Construire le contenu selon le type
          let content = '';
          let elements = [];
          
          if (isGrouped) {
            elements = item.elements;
            if (isMediaGroup) {
              // Pour les médias, montrer les URLs
              content = elements.map(el => el.src || el.title || '').join('\n');
            } else {
              // Pour les textes groupés
              content = elements.join('\n\n');
            }
          } else {
            content = item.contenu || item.content || item.apercu || '';
          }
          
          return {
            id: index + 1,
            title: titre,
            category: item.categorie || type,
            content: content,
            preview: item.apercu || content.substring(0, 150),
            isGrouped,
            isMediaGroup,
            isImage,
            isVideo,
            isLink,
            nbElements: item.nb_elements || 1,
            elements: elements,
            // Pour les images groupées
            imageSrc: isImage && elements.length > 0 ? elements[0].src : (item.url_media || null),
            videoSrc: isVideo && elements.length > 0 ? elements[0].src : null,
            linkHref: isLink ? (item.href || item.url || null) : null,
            rawData: item
          };
        });
        
        setResults(transformedResults);
        
      } catch (err) {
        console.error('Erreur lors du chargement des résultats:', err);
        setError(err.message || 'Erreur lors du chargement des résultats');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadResults();
  }, [sessionId, searchTerm, activeFilter]);
  
  // Déclencher le prompt d'export automatique si un format est pré-sélectionné
  useEffect(() => {
    if (!isLoading && results.length > 0 && preSelectedFormat && !exportTriggered.current) {
      exportTriggered.current = true;
      setShowExportPrompt(true);
    }
  }, [isLoading, results, preSelectedFormat]);
  
  const dataSource = results;
  
  // Filtrage des données - adapté aux données réelles du scraper
  const filteredProducts = dataSource.filter(item => {
    const searchLower = searchTerm.toLowerCase();
    const matchesSearch = 
      (item.title || '').toLowerCase().includes(searchLower) ||
      (item.category || '').toLowerCase().includes(searchLower) ||
      (item.content || '').toLowerCase().includes(searchLower) ||
      (item.preview || '').toLowerCase().includes(searchLower);
    
    if (activeFilter === 'all') return matchesSearch;
    if (activeFilter === 'new') return matchesSearch && item.stockStatus === 'success';
    if (activeFilter === 'errors') return matchesSearch && item.stockStatus === 'error';
    return matchesSearch;
  });

  // Pagination
  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedProducts = filteredProducts.slice(startIndex, startIndex + itemsPerPage);

  // Gestion de la sélection
  const handleSelectItem = (itemId) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedItems(newSelected);
    setSelectAll(newSelected.size === filteredProducts.length);
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(filteredProducts.map(item => item.id)));
    }
    setSelectAll(!selectAll);
  };

  const handleSelectPage = () => {
    const newSelected = new Set(selectedItems);
    const pageItemIds = paginatedProducts.map(item => item.id);
    const allPageSelected = pageItemIds.every(id => selectedItems.has(id));
    
    if (allPageSelected) {
      pageItemIds.forEach(id => newSelected.delete(id));
    } else {
      pageItemIds.forEach(id => newSelected.add(id));
    }
    setSelectedItems(newSelected);
  };

  // Export des éléments sélectionnés
  const handleExportSelected = async (format) => {
    if (selectedItems.size === 0) {
      alert('Veuillez sélectionner au moins un élément à exporter');
      return;
    }

    const selectedData = results.filter(item => selectedItems.has(item.id));
    let content, mimeType, extension;

    if (format === 'json') {
      content = JSON.stringify(selectedData, null, 2);
      mimeType = 'application/json';
      extension = 'json';
    } else if (format === 'pdf') {
      // Export PDF
      await generatePDF(selectedData, `scraping_session_${sessionId}`);
      return;
    } else if (format === 'csv') {
      const headers = ['ID', 'Titre', 'Contenu', 'Type', 'URL'];
      const rows = selectedData.map(item => [
        item.id,
        `"${(item.title || '').replace(/"/g, '""')}"`,
        `"${(item.content || item.preview || '').replace(/"/g, '""')}"`,
        item.category || 'text',
        item.url || '-'
      ]);
      content = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      mimeType = 'text/csv';
      extension = 'csv';
    } else {
      // Excel - export as CSV with BOM for Excel compatibility
      const headers = ['ID', 'Titre', 'Contenu', 'Type', 'URL'];
      const rows = selectedData.map(item => [
        item.id,
        `"${(item.title || '').replace(/"/g, '""')}"`,
        `"${(item.content || item.preview || '').replace(/"/g, '""')}"`,
        item.category || 'text',
        item.url || '-'
      ]);
      content = '\uFEFF' + [headers.join(';'), ...rows.map(r => r.join(';'))].join('\n');
      mimeType = 'text/csv;charset=utf-8';
      extension = 'csv';
    }

    // Utiliser File System Access API si disponible pour choisir l'emplacement
    await saveFile(content, `selection_${selectedItems.size}_items.${extension}`, mimeType);
  };

  // Fonction pour sauvegarder avec choix d'emplacement
  const saveFile = async (content, defaultName, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    
    // Essayer d'utiliser File System Access API (Chrome/Edge moderne)
    if ('showSaveFilePicker' in window) {
      try {
        const extension = defaultName.split('.').pop();
        const handle = await window.showSaveFilePicker({
          suggestedName: defaultName,
          types: [{
            description: extension.toUpperCase() + ' File',
            accept: { [mimeType]: ['.' + extension] }
          }]
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        return;
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.warn('File System Access API failed, falling back to download:', err);
        } else {
          return; // User cancelled
        }
      }
    }
    
    // Fallback: téléchargement classique
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = defaultName;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Générer un PDF avec les données
  const generatePDF = async (data, filename) => {
    // Organiser les données par catégorie pour un rapport structuré
    const categoryIcons = {
      'main_headings': '📌',
      'section_headings': '📑',
      'sub_headings': '📎',
      'paragraphs': '📝',
      'links': '🔗',
      'buttons': '🔘',
      'lists': '📋',
      'navigation': '🧭',
      'footer': '📄',
      'code': '💻',
      'other': '📦',
      'images': '🖼️',
      'image': '🖼️',
      'videos': '🎬',
      'video': '🎬',
      'audios': '🎵',
      'documents': '📄',
      'text': '📝'
    };

    const categoryNames = {
      'main_headings': 'Titres Principaux',
      'section_headings': 'Titres de Section',
      'sub_headings': 'Sous-titres',
      'paragraphs': 'Paragraphes',
      'links': 'Liens',
      'buttons': 'Boutons',
      'lists': 'Listes',
      'navigation': 'Navigation',
      'footer': 'Pied de page',
      'code': 'Code',
      'other': 'Autres contenus',
      'images': 'Images',
      'image': 'Images',
      'videos': 'Vidéos',
      'video': 'Vidéos',
      'audios': 'Audio',
      'documents': 'Documents',
      'text': 'Texte'
    };

    // Générer le HTML pour les images
    const generateImageGrid = (item) => {
      if (!item.isImage || !item.elements || item.elements.length === 0) return '';
      
      // Utiliser TOUS les éléments (pas de limite)
      return `
        <div class="image-grid">
          ${item.elements.map(img => `
            <div class="image-card">
              <img src="${img.src}" alt="${img.alt || 'Image'}" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
              <div class="image-error" style="display:none;">❌ Image non chargée</div>
              <div class="image-caption">${img.alt || img.title || img.src?.split('/').pop()?.substring(0, 30) || 'Image'}</div>
            </div>
          `).join('')}
        </div>
      `;
    };

    // Générer le HTML pour les liens
    const generateLinksList = (item) => {
      if (!item.isLink || !item.elements || item.elements.length === 0) return '';
      
      // Utiliser TOUS les éléments (pas de limite)
      return `
        <div class="links-list">
          ${item.elements.map(link => `
            <div class="link-item">
              <span class="link-icon">🔗</span>
              <a href="${link.href || link.src || '#'}" target="_blank">${link.title || link.text || link.href || 'Lien'}</a>
              ${link.href ? `<span class="link-url">${link.href}</span>` : ''}
            </div>
          `).join('')}
        </div>
      `;
    };

    // Générer le contenu pour les éléments groupés (texte)
    const generateGroupedContent = (item) => {
      if (!item.isGrouped || !item.elements || item.elements.length === 0) return '';
      if (item.isImage || item.isLink) return '';
      
      // Utiliser TOUS les éléments (pas de limite)
      return `
        <ul class="content-list">
          ${item.elements.map(el => `
            <li>${typeof el === 'string' ? el : (el.text || el.title || JSON.stringify(el))}</li>
          `).join('')}
        </ul>
      `;
    };

    // Créer le contenu HTML pour le PDF
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="fr">
      <head>
        <meta charset="UTF-8">
        <title>Rapport de Scraping - ${filename}</title>
        <style>
          * { box-sizing: border-box; }
          body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 40px; 
            color: #333; 
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            background: #fff;
          }
          
          /* En-tête du rapport */
          .report-header {
            background: linear-gradient(135deg, #FF4D00 0%, #CC3D00 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
          }
          .report-header h1 {
            margin: 0 0 20px 0;
            font-size: 2em;
            display: flex;
            align-items: center;
            gap: 15px;
          }
          .report-meta {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            background: rgba(255,255,255,0.15);
            padding: 15px 20px;
            border-radius: 8px;
          }
          .report-meta-item {
            display: flex;
            gap: 8px;
          }
          .report-meta-label {
            opacity: 0.85;
          }
          .report-meta-value {
            font-weight: 600;
          }
          
          /* Section de résumé */
          .summary-section {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
          }
          .summary-section h2 {
            color: #495057;
            margin: 0 0 15px 0;
            font-size: 1.3em;
          }
          .summary-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
          }
          .stat-badge {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 10px 15px;
            display: flex;
            align-items: center;
            gap: 8px;
          }
          .stat-icon { font-size: 1.3em; }
          .stat-count { font-weight: 700; color: #FF4D00; }
          .stat-label { color: #6c757d; font-size: 0.9em; }
          
          /* Catégories de contenu */
          .category-section {
            margin-bottom: 35px;
            page-break-inside: avoid;
          }
          .category-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #FF4D00;
          }
          .category-icon { font-size: 1.5em; }
          .category-title { 
            font-size: 1.4em; 
            color: #333; 
            margin: 0;
            font-weight: 600;
          }
          .category-count {
            background: #FF4D00;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
          }
          
          /* Contenu des items */
          .content-box {
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 20px;
            margin-top: 10px;
          }
          .content-preview {
            color: #555;
            font-size: 0.95em;
            margin-bottom: 15px;
            padding: 12px;
            background: white;
            border-left: 4px solid #FF4D00;
            border-radius: 0 6px 6px 0;
          }
          
          /* Liste de contenu */
          .content-list {
            list-style: none;
            padding: 0;
            margin: 0;
          }
          .content-list li {
            padding: 10px 15px;
            background: white;
            border: 1px solid #eee;
            margin-bottom: 8px;
            border-radius: 6px;
            font-size: 0.95em;
          }
          .content-list li:hover {
            border-color: #FF4D00;
          }
          
          /* Grille d'images */
          .image-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 15px;
          }
          .image-card {
            background: white;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
            text-align: center;
          }
          .image-card img {
            width: 100%;
            height: 120px;
            object-fit: cover;
            display: block;
          }
          .image-error {
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f5f5f5;
            color: #999;
          }
          .image-caption {
            padding: 8px;
            font-size: 0.8em;
            color: #666;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            background: #fafafa;
          }
          
          /* Liste de liens */
          .links-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 15px;
          }
          .link-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 15px;
            background: white;
            border: 1px solid #eee;
            border-radius: 6px;
          }
          .link-icon { font-size: 1.1em; }
          .link-item a {
            color: #FF4D00;
            text-decoration: none;
            font-weight: 500;
          }
          .link-url {
            color: #999;
            font-size: 0.8em;
            margin-left: auto;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          
          /* Plus d'éléments */
          .more-items {
            color: #888;
            font-style: italic;
            text-align: center;
            padding: 10px;
            margin: 10px 0 0 0;
          }
          
          /* Pied de page du rapport */
          .report-footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #888;
            font-size: 0.9em;
          }
          .report-footer strong {
            color: #FF4D00;
          }
          
          /* Print styles */
          @media print {
            body { padding: 20px; }
            .category-section { page-break-inside: avoid; }
            .image-grid { grid-template-columns: repeat(3, 1fr); }
          }
        </style>
      </head>
      <body>
        <!-- En-tête du rapport -->
        <div class="report-header">
          <h1>📊 Rapport de Scraping</h1>
          <div class="report-meta">
            <div class="report-meta-item">
              <span class="report-meta-label">Session:</span>
              <span class="report-meta-value">#${sessionId}</span>
            </div>
            <div class="report-meta-item">
              <span class="report-meta-label">Date:</span>
              <span class="report-meta-value">${new Date().toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <div class="report-meta-item">
              <span class="report-meta-label">URL:</span>
              <span class="report-meta-value">${sessionInfo?.url || 'N/A'}</span>
            </div>
            <div class="report-meta-item">
              <span class="report-meta-label">Éléments:</span>
              <span class="report-meta-value">${data.length} catégories</span>
            </div>
          </div>
        </div>
        
        <!-- Résumé statistique -->
        <div class="summary-section">
          <h2>📈 Résumé de l'extraction</h2>
          <div class="summary-stats">
            ${data.map(item => `
              <div class="stat-badge">
                <span class="stat-icon">${categoryIcons[item.category] || '📦'}</span>
                <span class="stat-count">${item.nbElements || 1}</span>
                <span class="stat-label">${categoryNames[item.category] || item.category || 'Contenu'}</span>
              </div>
            `).join('')}
          </div>
        </div>
        
        <!-- Contenu par catégorie -->
        <h2 style="color: #333; margin-bottom: 25px;">📋 Données Extraites</h2>
        
        ${data.map((item, idx) => `
          <div class="category-section">
            <div class="category-header">
              <span class="category-icon">${categoryIcons[item.category] || '📦'}</span>
              <h3 class="category-title">${categoryNames[item.category] || item.title || 'Contenu'}</h3>
              ${item.nbElements > 1 ? `<span class="category-count">${item.nbElements} éléments</span>` : ''}
            </div>
            
            <div class="content-box">
              ${item.preview ? `
                <div class="content-preview">
                  ${item.preview.substring(0, 300)}${item.preview.length > 300 ? '...' : ''}
                </div>
              ` : ''}
              
              ${item.isImage ? generateImageGrid(item) : ''}
              ${item.isLink ? generateLinksList(item) : ''}
              ${!item.isImage && !item.isLink && item.isGrouped ? generateGroupedContent(item) : ''}
              ${!item.isGrouped && item.content ? `<p style="color: #555;">${item.content}</p>` : ''}
            </div>
          </div>
        `).join('')}
        
        <!-- Pied de page -->
        <div class="report-footer">
          <p>Généré par <strong>Scraper Pro</strong> — ${new Date().toLocaleString('fr-FR')}</p>
          <p>🌐 ${sessionInfo?.url || ''}</p>
        </div>
      </body>
      </html>
    `;
    
    // Ouvrir dans une nouvelle fenêtre pour impression/PDF
    const printWindow = window.open('', '_blank');
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    
    // Attendre le chargement des images puis déclencher l'impression
    printWindow.onload = () => {
      // Petit délai pour laisser les images se charger
      setTimeout(() => {
        printWindow.print();
      }, 1000);
    };
  };

  // Ouvrir la prévisualisation
  const openPreview = (item) => {
    setPreviewItem(item);
    setShowPreview(true);
  };

  const handleExport = async (format) => {
    if (!sessionId) {
      alert('Aucune session active pour l\'export');
      return;
    }
    
    // Ouvrir le modal de sélection au lieu d'exporter directement
    setExportModalFormat(format);
    setExportLimit(Math.min(results.length, 100)); // Par défaut 100 ou moins si moins de résultats
    setExportSelectedOnly(selectedItems.size > 0); // Si des items sont sélectionnés, activer par défaut
    setShowExportModal(true);
  };
  
  // Fonction d'export confirmée après sélection
  const handleConfirmExport = async () => {
    const format = exportModalFormat;
    if (!sessionId || !format) return;
    
    setShowExportModal(false);
    
    // Pour PDF, générer localement
    if (format.toLowerCase() === 'pdf') {
      setExportingFormat('pdf');
      try {
        // Filtrer les résultats selon la sélection
        const dataToExport = getFilteredDataForExport();
        await generatePDF(dataToExport, `scraping_session_${sessionId}`);
      } finally {
        setExportingFormat(null);
      }
      return;
    }
    
    // Définir l'état de chargement
    setExportingFormat(format.toLowerCase());
    
    try {
      // Préparer les IDs des éléments à exporter
      const itemsToExport = getFilteredDataForExport().map(item => item.id);
      
      const blob = await api.exportResults(sessionId, format.toLowerCase(), {
        item_ids: itemsToExport.length < results.length ? itemsToExport : null,
        limit: exportLimit
      });
      
      // Déterminer l'extension du fichier
      let extension = format.toLowerCase();
      if (format.toLowerCase() === 'zip_images') {
        extension = 'zip';
      }
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `results_${sessionId}.${extension}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
    } catch (error) {
      console.error('Erreur lors de l\'export:', error);
      alert(`Erreur lors de l'export ${format}: ${error.message || 'Erreur inconnue'}`);
    } finally {
      setExportingFormat(null);
    }
  };
  
  // Obtenir les données filtrées pour l'export
  const getFilteredDataForExport = () => {
    if (exportSelectedOnly && selectedItems.size > 0) {
      // Exporter uniquement les items sélectionnés
      return results.filter(item => selectedItems.has(item.id));
    } else {
      // Exporter selon la limite
      return results.slice(0, exportLimit);
    }
  };

  // Re-scraper le site avec la même configuration
  const handleRescrape = async () => {
    if (!sessionId) {
      alert('Aucune session à re-scraper');
      return;
    }
    
    if (!confirm('Voulez-vous relancer le scraping de ce site avec la même configuration ?')) {
      return;
    }
    
    try {
      const response = await api.rescrape(sessionId);
      
      if (response.new_session_id) {
        alert(`Nouveau scraping lancé ! Session #${response.new_session_id}`);
        // Rediriger vers la nouvelle session
        navigate(`/results?session=${response.new_session_id}`);
      }
    } catch (error) {
      console.error('Erreur lors du re-scraping:', error);
      alert(`Erreur: ${error.message || 'Impossible de relancer le scraping'}`);
    }
  };
  return (
    <div className="app-container">
      {/* Sidebar - SEULEMENT le logo */}
      <aside className="sidebar">
        <div className="logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <div className="logo-icon">⚡</div>
          SCRAPER PRO
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header className="page-header">
          <div>
            <h1 className="page-title">Résultats du scraping</h1>
            <p className="session-id">Session #{sessionId || 'SCR-2026-001247'}</p>
          </div>
          <div className="session-info">
            <div className="info-item">
              <span className="info-label">Statut</span>
              <span className={`status-badge status-${sessionInfo?.status || 'success'}`}>
                {sessionInfo?.status === 'completed' ? '✓ Terminé' : 
                 sessionInfo?.status === 'running' ? '⏳ En cours' : 
                 sessionInfo?.status === 'error' ? '✕ Erreur' : '✓ Terminé'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Date</span>
              <span className="info-value">{sessionInfo?.date || '02/02/2026'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Éléments</span>
              <span className="info-value">{sessionInfo?.items || results.length || '0'}</span>
            </div>
            <button 
              className="btn-rescrape"
              onClick={handleRescrape}
              title="Lancer un nouveau scraping avec la même configuration"
            >
              <span>🔄</span>
              Re-scraper
            </button>
          </div>
        </header>

        {/* Controls Bar */}
        <div className="controls-bar">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              className="search-input"
              placeholder="Rechercher dans les résultats..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <button
              className={`filter-btn ${activeFilter === 'all' ? 'active' : ''}`}
              onClick={() => setActiveFilter('all')}
            >
              <span>📦</span>
              Tous
            </button>
            <button
              className={`filter-btn ${activeFilter === 'new' ? 'active' : ''}`}
              onClick={() => setActiveFilter('new')}
            >
              <span>⚡</span>
              En stock
            </button>
            <button
              className={`filter-btn ${activeFilter === 'errors' ? 'active' : ''}`}
              onClick={() => setActiveFilter('errors')}
            >
              <span>⚠️</span>
              Erreurs
            </button>
          </div>

          <div className="export-group">
            <button 
              className={`export-btn ${exportingFormat === 'csv' ? 'exporting' : ''}`} 
              onClick={() => handleExport('CSV')}
              disabled={exportingFormat !== null}
            >
              <span>{exportingFormat === 'csv' ? '⏳' : '📄'}</span>
              {exportingFormat === 'csv' ? 'Export...' : 'CSV'}
            </button>
            <button 
              className={`export-btn ${exportingFormat === 'excel' ? 'exporting' : ''}`} 
              onClick={() => handleExport('Excel')}
              disabled={exportingFormat !== null}
            >
              <span>{exportingFormat === 'excel' ? '⏳' : '📊'}</span>
              {exportingFormat === 'excel' ? 'Export...' : 'Excel'}
            </button>
            <button 
              className={`export-btn ${exportingFormat === 'json' ? 'exporting' : ''}`} 
              onClick={() => handleExport('JSON')}
              disabled={exportingFormat !== null}
            >
              <span>{exportingFormat === 'json' ? '⏳' : '🔧'}</span>
              {exportingFormat === 'json' ? 'Export...' : 'JSON'}
            </button>
            <button 
              className={`export-btn export-btn-pdf ${exportingFormat === 'pdf' ? 'exporting' : ''}`} 
              onClick={() => handleExport('PDF')}
              disabled={exportingFormat !== null}
            >
              <span>{exportingFormat === 'pdf' ? '⏳' : '📕'}</span>
              {exportingFormat === 'pdf' ? 'Export...' : 'PDF'}
            </button>
            <button 
              className={`export-btn ${exportingFormat === 'xml' ? 'exporting' : ''}`} 
              onClick={() => handleExport('XML')}
              disabled={exportingFormat !== null}
            >
              <span>{exportingFormat === 'xml' ? '⏳' : '📋'}</span>
              {exportingFormat === 'xml' ? 'Export...' : 'XML'}
            </button>
            <button 
              className={`export-btn ${includeImagesZip ? 'export-btn-highlight' : ''} ${exportingFormat === 'zip_images' ? 'exporting' : ''}`} 
              onClick={() => handleExport('ZIP_IMAGES')}
              disabled={exportingFormat !== null}
              title={exportingFormat === 'zip_images' ? 'Téléchargement des images en cours...' : (includeImagesZip ? 'Option sélectionnée depuis la configuration' : 'Télécharger les images en ZIP')}
            >
              <span>{exportingFormat === 'zip_images' ? '⏳' : '🖼️'}</span>
              {exportingFormat === 'zip_images' ? 'Téléchargement...' : 'ZIP Images'}
              {includeImagesZip && !exportingFormat && <span className="highlight-badge">★</span>}
            </button>
          </div>
        </div>

        {/* Barre de sélection - visible quand des éléments sont sélectionnés */}
        {selectedItems.size > 0 && (
          <div className="selection-bar">
            <div className="selection-info">
              <span className="selection-count">✓ {selectedItems.size} élément(s) sélectionné(s)</span>
              <button className="clear-selection-btn" onClick={() => { setSelectedItems(new Set()); setSelectAll(false); }}>
                ✕ Désélectionner
              </button>
            </div>
            <div className="selection-actions">
              <span className="export-label">Exporter la sélection :</span>
              <button className="export-selection-btn" onClick={() => handleExportSelected('csv')}>
                📄 CSV
              </button>
              <button className="export-selection-btn" onClick={() => handleExportSelected('excel')}>
                📊 Excel
              </button>
              <button className="export-selection-btn" onClick={() => handleExportSelected('json')}>
                🔧 JSON
              </button>
              <button className="export-selection-btn export-btn-pdf" onClick={() => handleExportSelected('pdf')}>
                📕 PDF
              </button>
            </div>
          </div>
        )}

        {/* Loading/Error States */}
        {isLoading && (
          <div className="card" style={{padding: '3rem', textAlign: 'center'}}>
            <div style={{fontSize: '2rem', marginBottom: '1rem'}}>⏳</div>
            <h3>Chargement des résultats...</h3>
            <p style={{color: 'var(--text-muted)', marginTop: '0.5rem'}}>Veuillez patienter</p>
          </div>
        )}
        
        {/* État sans session */}
        {!isLoading && !sessionId && (
          <div className="empty-state-container">
            <div className="empty-state-icon">📂</div>
            <h2 className="empty-state-title">Aucune session de scraping</h2>
            <p className="empty-state-text">
              Vous n'avez pas de session de scraping active. Lancez une nouvelle analyse pour voir les résultats ici.
            </p>
            <div className="empty-state-actions">
              <button className="empty-state-btn primary" onClick={() => navigate('/analysis')}>
                🔍 Lancer une analyse
              </button>
              <button className="empty-state-btn secondary" onClick={() => navigate('/dashboard')}>
                📊 Aller au Dashboard
              </button>
            </div>
          </div>
        )}
        
        {/* État session trouvée mais pas de données */}
        {!isLoading && !error && sessionId && results.length === 0 && (
          <div className="empty-state-container">
            <div className="empty-state-icon">📭</div>
            <h2 className="empty-state-title">Aucune donnée extraite</h2>
            <p className="empty-state-text">
              La session #{sessionId} existe mais ne contient pas de données.
              {sessionInfo?.status === 'in_progress' && (
                <><br/><strong>Le scraping est peut-être encore en cours...</strong></>
              )}
            </p>
            <div className="empty-state-actions">
              <button className="empty-state-btn secondary" onClick={() => window.location.reload()}>
                🔄 Rafraîchir
              </button>
              <button className="empty-state-btn primary" onClick={() => navigate('/analysis')}>
                🔍 Nouvelle analyse
              </button>
              <button className="empty-state-btn secondary" onClick={() => navigate('/dashboard')}>
                📊 Dashboard
              </button>
            </div>
          </div>
        )}
        
        {error && (
          <div className="error-alert">
            <div className="error-icon">⚠️</div>
            <div className="error-content">
              <h4>Erreur de chargement</h4>
              <p>{error}</p>
              <div className="error-actions">
                <button className="error-btn" onClick={() => navigate('/dashboard')}>
                  📊 Retour au Dashboard
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Data Table */}
        {!isLoading && !error && sessionId && results.length > 0 && (
        <div className="table-container">
          {/* Dossier du site scrapé */}
          <div className="folder-header">
            <div className="folder-icon">📁</div>
            <div className="folder-info">
              <h3 className="folder-name">{sessionInfo?.url ? new URL(sessionInfo.url).hostname : 'Site scrapé'}</h3>
              <span className="folder-url">{sessionInfo?.url || ''}</span>
            </div>
            <div className="folder-stats">
              <span className="folder-stat">
                <span className="stat-value">{filteredProducts.length}</span>
                <span className="stat-label">catégories</span>
              </span>
              <span className="folder-stat">
                <span className="stat-value">{filteredProducts.reduce((acc, item) => acc + (item.nbElements || 1), 0)}</span>
                <span className="stat-label">éléments</span>
              </span>
            </div>
          </div>
          
          <div className="folder-content">
            <div className="table-header">
              <h4 className="table-title">📂 Contenu du dossier</h4>
              <span className="table-count">
                Affichage {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredProducts.length)} sur {filteredProducts.length} éléments
              </span>
            </div>

          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '50px' }}>
                  <input 
                    type="checkbox" 
                    className="select-checkbox"
                    checked={paginatedProducts.length > 0 && paginatedProducts.every(item => selectedItems.has(item.id))}
                    onChange={handleSelectPage}
                    title="Sélectionner cette page"
                  />
                </th>
                <th style={{ width: '50px' }}>#</th>
                <th>Aperçu</th>
                <th>Contenu</th>
                <th>Type</th>
                <th style={{ width: '100px' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedProducts.map((item) => (
                <tr key={item.id} className={selectedItems.has(item.id) ? 'row-selected' : ''}>
                  <td>
                    <input 
                      type="checkbox" 
                      className="select-checkbox"
                      checked={selectedItems.has(item.id)}
                      onChange={() => handleSelectItem(item.id)}
                    />
                  </td>
                  <td>{item.id}</td>
                  <td>
                    {/* Aperçu visuel selon le type */}
                    <div className="cell-preview">
                      {item.isImage && item.imageSrc ? (
                        <img src={item.imageSrc} alt={item.title} className="preview-thumbnail" onError={(e) => e.target.style.display='none'} />
                      ) : item.isImage ? (
                        <div className="preview-icon" style={{ background: getCategoryConfig('images').color + '20', color: getCategoryConfig('images').color }}>🖼️</div>
                      ) : item.isVideo ? (
                        <div className="preview-icon" style={{ background: getCategoryConfig('videos').color + '20', color: getCategoryConfig('videos').color }}>🎬</div>
                      ) : item.isLink ? (
                        <div className="preview-icon" style={{ background: getCategoryConfig('links').color + '20', color: getCategoryConfig('links').color }}>🔗</div>
                      ) : (
                        <div className="preview-icon" style={{ background: getCategoryConfig(item.category).color + '20' }}>
                          {getCategoryConfig(item.category).icon}
                        </div>
                      )}
                      {item.nbElements > 1 && (
                        <span className="element-count">{item.nbElements}</span>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="cell-content-wrapper">
                      <div className="cell-title-main">
                        {getCategoryConfig(item.category).icon} {getCategoryConfig(item.category).name}
                        {item.nbElements > 1 && <span className="title-count">({item.nbElements})</span>}
                      </div>
                      <div className="cell-preview-text">{item.preview?.substring(0, 80) || '-'}</div>
                    </div>
                  </td>
                  <td>
                    <span 
                      className="type-badge" 
                      style={{ 
                        background: getCategoryConfig(item.category).color + '20',
                        color: getCategoryConfig(item.category).color,
                        borderColor: getCategoryConfig(item.category).color + '40'
                      }}
                    >
                      {getCategoryConfig(item.category).icon} {getCategoryConfig(item.category).name}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="action-btn preview-btn" onClick={() => openPreview(item)} title="Prévisualiser">
                        👁️
                      </button>
                      {item.isMediaGroup && item.elements?.length > 0 && (
                        <span className="elements-badge">{item.nbElements}</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="pagination">
            <div className="pagination-info">
              Affichage {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredProducts.length)} sur {filteredProducts.length} éléments
            </div>
            <div className="pagination-controls">
              <button
                className="page-btn"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                ◀
              </button>
              {[...Array(Math.min(5, totalPages))].map((_, idx) => {
                const pageNum = idx + 1;
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
              {totalPages > 5 && (
                <>
                  <button className="page-btn">...</button>
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
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
              >
                ▶
              </button>
            </div>
          </div>
          </div>
        </div>
        )}

        {/* Modal de prévisualisation */}
        {showPreview && previewItem && (
          <div className="preview-modal-overlay" onClick={() => setShowPreview(false)}>
            <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
              <div className="preview-modal-header">
                <h3>{previewItem.title || 'Prévisualisation'}</h3>
                <button className="preview-close-btn" onClick={() => setShowPreview(false)}>✕</button>
              </div>
              
              <div className="preview-modal-body">
                {/* Info groupement */}
                {previewItem.isGrouped && (
                  <div className="preview-group-info">
                    <span className="group-badge">📦 {previewItem.nbElements} éléments groupés</span>
                  </div>
                )}

                {/* Contenu principal */}
                <div className="preview-content-section">
                  {/* Galerie d'images groupées */}
                  {previewItem.isImage && previewItem.isGrouped && previewItem.elements?.length > 0 ? (
                    <div className="preview-gallery">
                      <h4>🖼️ Images ({previewItem.elements.length})</h4>
                      <div className="gallery-grid">
                        {previewItem.elements.slice(0, 12).map((img, idx) => (
                          <div key={idx} className="gallery-item">
                            <img src={img.src} alt={img.alt || `Image ${idx+1}`} onError={(e) => e.target.style.display='none'} />
                            <span className="gallery-alt">{img.alt || img.src.split('/').pop()}</span>
                          </div>
                        ))}
                      </div>
                      {previewItem.elements.length > 12 && (
                        <p className="gallery-more">+ {previewItem.elements.length - 12} autres images</p>
                      )}
                    </div>
                  ) : previewItem.isVideo ? (
                    <div className="preview-video-container">
                      {previewItem.elements?.length > 0 ? (
                        previewItem.elements.slice(0, 4).map((vid, idx) => (
                          <div key={idx} className="video-item">
                            <video controls className="preview-video-full">
                              <source src={vid.src} />
                            </video>
                            <p className="preview-url">{vid.src}</p>
                          </div>
                        ))
                      ) : previewItem.videoSrc ? (
                        <video controls className="preview-video-full">
                          <source src={previewItem.videoSrc} />
                        </video>
                      ) : null}
                    </div>
                  ) : previewItem.isGrouped && previewItem.elements?.length > 0 ? (
                    /* Liste de contenus groupés */
                    <div className="preview-list-container">
                      <ul className="preview-list">
                        {previewItem.elements.slice(0, 30).map((el, idx) => (
                          <li key={idx} className="preview-list-item">
                            {typeof el === 'string' ? el : (el.title || el.src || JSON.stringify(el))}
                          </li>
                        ))}
                      </ul>
                      {previewItem.elements.length > 30 && (
                        <p className="preview-more">+ {previewItem.elements.length - 30} autres éléments</p>
                      )}
                    </div>
                  ) : (
                    <div className="preview-text-container">
                      <p className="preview-text-full">{previewItem.content || previewItem.preview}</p>
                    </div>
                  )}
                </div>

                {/* Données brutes */}
                <details className="preview-raw-data">
                  <summary>📋 Données brutes (JSON)</summary>
                  <pre>{JSON.stringify(previewItem.rawData, null, 2)}</pre>
                </details>
              </div>

              <div className="preview-modal-footer">
                <button className="preview-action-btn" onClick={() => {
                  navigator.clipboard.writeText(previewItem.content || previewItem.preview || '');
                  alert('Copié dans le presse-papier !');
                }}>
                  📋 Copier le contenu
                </button>
                {(previewItem.url && previewItem.url !== '-') && (
                  <a href={previewItem.url} target="_blank" rel="noopener noreferrer" className="preview-action-btn">
                    🔗 Ouvrir le lien
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* Modal d'export automatique (format pré-sélectionné depuis Analysis) */}
        {showExportPrompt && preSelectedFormat && (
          <div className="preview-modal-overlay" onClick={() => setShowExportPrompt(false)}>
            <div className="export-prompt-modal" onClick={e => e.stopPropagation()}>
              <div className="export-prompt-header">
                <h3>📦 Export des résultats</h3>
                <button className="preview-close-btn" onClick={() => setShowExportPrompt(false)}>×</button>
              </div>
              <div className="export-prompt-body">
                <p>
                  Vous avez choisi le format <strong>{preSelectedFormat.toUpperCase()}</strong> avant le scraping.
                </p>
                <p>Voulez-vous exporter les {results.length} résultats maintenant ?</p>
              </div>
              <div className="export-prompt-actions">
                <button 
                  className="export-prompt-btn primary"
                  onClick={() => {
                    handleExport(preSelectedFormat);
                    setShowExportPrompt(false);
                  }}
                >
                  ✅ Exporter en {preSelectedFormat.toUpperCase()}
                </button>
                <button 
                  className="export-prompt-btn secondary"
                  onClick={() => setShowExportPrompt(false)}
                >
                  ❌ Plus tard
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Modal de sélection pour l'export */}
        {showExportModal && exportModalFormat && (
          <div className="preview-modal-overlay" onClick={() => setShowExportModal(false)}>
            <div className="export-selection-modal" onClick={e => e.stopPropagation()} style={{
              background: 'linear-gradient(135deg, #141419, #1a1a20)',
              border: '1px solid rgba(255, 77, 0, 0.3)',
              borderRadius: '16px',
              padding: '2rem',
              maxWidth: '500px',
              width: '90%'
            }}>
              <div className="export-prompt-header">
                <h3 style={{ color: '#FF4D00', marginBottom: '0.5rem' }}>
                  📦 Configuration de l'export {exportModalFormat.toUpperCase()}
                </h3>
                <button className="preview-close-btn" onClick={() => setShowExportModal(false)}>×</button>
              </div>
              
              <div style={{ marginTop: '1.5rem', color: '#A0A0B0' }}>
                <p style={{ marginBottom: '1rem' }}>
                  Total de résultats disponibles: <strong style={{ color: '#00E5FF' }}>{results.length}</strong>
                </p>
                
                {selectedItems.size > 0 && (
                  <div style={{ 
                    marginBottom: '1.5rem',
                    padding: '1rem',
                    background: 'rgba(0, 229, 255, 0.1)',
                    border: '1px solid rgba(0, 229, 255, 0.3)',
                    borderRadius: '8px'
                  }}>
                    <label style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem',
                      cursor: 'pointer',
                      color: '#00E5FF'
                    }}>
                      <input
                        type="checkbox"
                        checked={exportSelectedOnly}
                        onChange={(e) => setExportSelectedOnly(e.target.checked)}
                        style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                      />
                      <span>
                        Exporter uniquement les {selectedItems.size} élément{selectedItems.size > 1 ? 's' : ''} sélectionné{selectedItems.size > 1 ? 's' : ''}
                      </span>
                    </label>
                  </div>
                )}
                
                {!exportSelectedOnly && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', color: '#FFFFFF' }}>
                      Nombre d'éléments à exporter:
                    </label>
                    <input
                      type="range"
                      min="1"
                      max={results.length}
                      value={exportLimit}
                      onChange={(e) => setExportLimit(parseInt(e.target.value))}
                      style={{
                        width: '100%',
                        accentColor: '#FF4D00',
                        marginBottom: '0.5rem'
                      }}
                    />
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.9rem'
                    }}>
                      <span>1</span>
                      <span style={{ color: '#FF4D00', fontWeight: '600', fontSize: '1.1rem' }}>
                        {exportLimit}
                      </span>
                      <span>{results.length}</span>
                    </div>
                  </div>
                )}
                
                <div style={{
                  padding: '1rem',
                  background: 'rgba(255, 77, 0, 0.1)',
                  border: '1px solid rgba(255, 77, 0, 0.3)',
                  borderRadius: '8px',
                  marginBottom: '1.5rem'
                }}>
                  <p style={{ margin: 0, fontSize: '0.9rem' }}>
                    📊 {exportSelectedOnly && selectedItems.size > 0 
                      ? `${selectedItems.size} élément${selectedItems.size > 1 ? 's' : ''} sélectionné${selectedItems.size > 1 ? 's' : ''}`
                      : `${exportLimit} premier${exportLimit > 1 ? 's' : ''} élément${exportLimit > 1 ? 's' : ''}`
                    } sera{(exportSelectedOnly ? selectedItems.size : exportLimit) > 1 ? 'ont' : ''} exporté{(exportSelectedOnly ? selectedItems.size : exportLimit) > 1 ? 's' : ''}.
                  </p>
                </div>
              </div>
              
              <div className="export-prompt-actions" style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                <button 
                  className="export-prompt-btn primary"
                  onClick={handleConfirmExport}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    background: '#FF4D00',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  ✅ Exporter
                </button>
                <button 
                  className="export-prompt-btn secondary"
                  onClick={() => setShowExportModal(false)}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    background: 'rgba(160, 160, 176, 0.2)',
                    border: '1px solid #606070',
                    borderRadius: '8px',
                    color: '#A0A0B0',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  ❌ Annuler
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Results;
