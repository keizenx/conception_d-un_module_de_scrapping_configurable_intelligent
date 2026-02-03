// frontend/src/components/ContentSelector/ContentSelector.jsx
// Sélecteur de types de contenus à scraper
// Permet de choisir articles, commentaires, produits, etc.
// RELEVANT FILES: Analysis.jsx, Results.jsx

import { useState } from 'react';
import './ContentSelector.css';

const ContentSelector = ({ scrapableContent, onSelectionChange }) => {
  const [selectedTypes, setSelectedTypes] = useState(['all']); // Par défaut tout sélectionné
  const [showDetails, setShowDetails] = useState({});

  if (!scrapableContent || !scrapableContent.detected_types || scrapableContent.detected_types.length === 0) {
    return (
      <div className="content-selector empty">
        <span className="material-icons-outlined md-48">info</span>
        <p>Aucun type de contenu spécifique détecté</p>
        <small>Le scraping complet du site sera effectué</small>
      </div>
    );
  }

  const handleToggleType = (type) => {
    let newSelection;
    
    if (type === 'all') {
      newSelection = ['all'];
    } else {
      // Retirer 'all' si on sélectionne un type spécifique
      const withoutAll = selectedTypes.filter(t => t !== 'all');
      
      if (withoutAll.includes(type)) {
        newSelection = withoutAll.filter(t => t !== type);
        // Si plus rien, revenir à 'all'
        if (newSelection.length === 0) {
          newSelection = ['all'];
        }
      } else {
        newSelection = [...withoutAll, type];
      }
    }
    
    setSelectedTypes(newSelection);
    onSelectionChange?.(newSelection);
  };

  const toggleDetails = (type) => {
    setShowDetails(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  const { detected_types, total_types, recommended_action, structure_complexity } = scrapableContent;

  return (
    <div className="content-selector">
      <div className="selector-header">
        <h3>
          <span className="material-icons-outlined">category</span>
          Types de Contenus Disponibles
        </h3>
        <div className="selector-stats">
          <div className="stat">
            <span className="material-icons-outlined">analytics</span>
            <span>{total_types} types détectés</span>
          </div>
          <div className="stat">
            <span className="material-icons-outlined">
              {structure_complexity === 'simple' ? 'check_circle' : structure_complexity === 'medium' ? 'info' : 'warning'}
            </span>
            <span>Complexité: {structure_complexity}</span>
          </div>
        </div>
      </div>

      <div className="selection-mode">
        <button
          className={`mode-btn ${selectedTypes.includes('all') ? 'active' : ''}`}
          onClick={() => handleToggleType('all')}
        >
          <span className="material-icons-outlined">select_all</span>
          Tout Scraper
        </button>
        <button
          className={`mode-btn ${!selectedTypes.includes('all') ? 'active' : ''}`}
          onClick={() => {
            // Basculer en mode sélectif
            if (selectedTypes.includes('all')) {
              setSelectedTypes([detected_types[0]?.type || '']);
            }
          }}
        >
          <span className="material-icons-outlined">checklist</span>
          Sélection Personnalisée
        </button>
      </div>

      {recommended_action === 'full_site' && (
        <div className="recommendation">
          <span className="material-icons-outlined">lightbulb</span>
          <p>Structure complexe détectée - Le scraping complet est recommandé</p>
        </div>
      )}

      <div className="content-types-grid">
        {detected_types.map((content) => {
          const isSelected = selectedTypes.includes('all') || selectedTypes.includes(content.type);
          const isExpanded = showDetails[content.type];

          return (
            <div
              key={content.type}
              className={`content-type-card ${isSelected ? 'selected' : ''}`}
            >
              <div className="card-header" onClick={() => handleToggleType(content.type)}>
                <div className="card-icon">
                  <span className={`material-icons-outlined ${isSelected ? 'active' : ''}`}>
                    {content.icon}
                  </span>
                </div>
                <div className="card-info">
                  <h4>{content.name}</h4>
                  <p className="description">{content.description}</p>
                  <div className="card-meta">
                    <span className="count">
                      <span className="material-icons-outlined md-18">tag</span>
                      {content.count} éléments
                    </span>
                    <span className="confidence">
                      <span className="material-icons-outlined md-18">verified</span>
                      {(content.confidence * 100).toFixed(0)}% confiance
                    </span>
                  </div>
                </div>
                <div className="card-actions">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => {}}
                    className="type-checkbox"
                  />
                  <button
                    className="details-toggle"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleDetails(content.type);
                    }}
                  >
                    <span className="material-icons-outlined">
                      {isExpanded ? 'expand_less' : 'expand_more'}
                    </span>
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className="card-details">
                  <div className="fields-section">
                    <h5>
                      <span className="material-icons-outlined md-18">label</span>
                      Champs Disponibles
                    </h5>
                    <div className="fields-list">
                      {content.fields.map((field) => (
                        <span key={field} className="field-tag">
                          {field}
                        </span>
                      ))}
                    </div>
                  </div>

                  {content.sample && Object.keys(content.sample).length > 0 && (
                    <div className="sample-section">
                      <h5>
                        <span className="material-icons-outlined md-18">preview</span>
                        Aperçu
                      </h5>
                      <div className="sample-data">
                        {Object.entries(content.sample).map(([key, value]) => (
                          <div key={key} className="sample-item">
                            <strong>{key}:</strong>
                            <span>{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="selection-summary">
        <span className="material-icons-outlined">info</span>
        <span>
          {selectedTypes.includes('all')
            ? `Tous les contenus seront scrapés (${total_types} types)`
            : `${selectedTypes.length} type(s) sélectionné(s)`}
        </span>
      </div>
    </div>
  );
};

export default ContentSelector;
