// src/components/SmartInputBar/SmartInputBar.jsx
import React, { useState, useEffect } from 'react';
import './SmartInputBar.css';

const SmartInputBar = ({ 
  onAnalyze, 
  placeholder = "Entrez une URL, sélecteur CSS ou HTML brut...",
  defaultValue = "",
  defaultType = "url"
}) => {
  const [input, setInput] = useState(defaultValue);
  const [inputType, setInputType] = useState(defaultType);
  const [isValid, setIsValid] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  // Types d'entrée disponibles
  const inputTypes = [
    { id: 'url', label: 'URL', icon: 'fas fa-link', description: 'Analyser un site web complet' },
    { id: 'selector', label: 'Sélecteur CSS', icon: 'fas fa-code', description: 'Cibler des éléments spécifiques' },
    { id: 'html', label: 'HTML Brut', icon: 'fas fa-file-code', description: 'Coller du HTML à analyser' }
  ];

  // Validation des entrées
  const validateInput = (value, type) => {
    if (!value.trim()) {
      setErrorMessage('Veuillez entrer une valeur');
      return false;
    }

    switch (type) {
      case 'url':
        try {
          const url = new URL(value);
          const isValidUrl = url.protocol === 'http:' || url.protocol === 'https:';
          if (!isValidUrl) {
            setErrorMessage('URL doit commencer par http:// ou https://');
            return false;
          }
          setErrorMessage('');
          return true;
        } catch {
          setErrorMessage('URL invalide. Ex: https://exemple.com');
          return false;
        }

      case 'selector':
        // Validation basique des sélecteurs CSS
        const selector = value.trim();
        if (selector.length < 2) {
          setErrorMessage('Sélecteur trop court');
          return false;
        }
        if (!selector.match(/^[a-zA-Z0-9#\.\[\]:_\-\s>+~=]+$/)) {
          setErrorMessage('Sélecteur CSS invalide');
          return false;
        }
        setErrorMessage('');
        return true;

      case 'html':
        // Validation basique HTML
        const html = value.trim();
        if (html.length < 10) {
          setErrorMessage('HTML trop court pour analyse');
          return false;
        }
        if (!html.includes('<') || !html.includes('>')) {
          setErrorMessage('Ce ne semble pas être du HTML valide');
          return false;
        }
        setErrorMessage('');
        return true;

      default:
        return true;
    }
  };

  // Exemples pour chaque type
 

  const getExamples = () => {
  switch (inputType) {
    case 'url':
      return [
        'https://amazon.com/electronics',      // E-commerce
        'https://themeforest.net',             // Templates
        'https://medium.com',                  // Blog
        'https://github.com/trending',          // GitHub
        'https://news.ycombinator.com'         // News
      ];
    case 'selector':
      return [
        '.product-card',                       // E-commerce
        '.template-item',                      // Templates
        'article',                             // Blog
        '.repo-item',                          // GitHub
        'div.content > p',                     // Générique
        '#price',                              // Prix
        'h1.title',                            // Titre
        '.review-item',                        // Avis
        '.category-link'                       // Catégorie
      ];
    case 'html':
      return [
        '<div class="product"><h3>iPhone 15</h3><span class="price">999€</span></div>', // E-commerce
        '<div class="template"><h3>Template Pro</h3><span class="price">49$</span></div>', // Templates
        '<article><h2>Titre Article</h2><p>Contenu intéressant...</p></article>', // Blog
        '<div class="repo"><h3>repository-name</h3><span class="stars">⭐ 245</span></div>' // GitHub
      ];
    default:
      return [];
  }
};


  // Gérer le changement d'entrée
  const handleInputChange = (e) => {
    const value = e.target.value;
    setInput(value);
    setIsValid(validateInput(value, inputType));
  };

  // Gérer le changement de type
  const handleTypeChange = (type) => {
    setInputType(type);
    setIsValid(validateInput(input, type));
  };

  // Soumettre l'analyse
  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateInput(input, inputType) && onAnalyze) {
      onAnalyze(input, inputType);
    }
  };

  // Charger un exemple
  const loadExample = (example) => {
    setInput(example);
    setIsValid(validateInput(example, inputType));
  };

  return (
    <div className="smart-input-container">
      {/* Sélecteur de type */}
      <div className="input-type-selector">
        {inputTypes.map((type) => (
          <button
            key={type.id}
            className={`type-btn ${inputType === type.id ? 'active' : ''}`}
            onClick={() => handleTypeChange(type.id)}
            type="button"
          >
            <i className={type.icon}></i>
            {type.label}
          </button>
        ))}
      </div>

      {/* Description du type sélectionné */}
      <div className="type-description">
        <p>
          <i className={inputTypes.find(t => t.id === inputType)?.icon}></i>
          {inputTypes.find(t => t.id === inputType)?.description}
        </p>
      </div>

      {/* Zone de saisie principale */}
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-wrapper">
          {inputType === 'html' ? (
            <textarea
              className={`smart-input ${!isValid ? 'error' : ''}`}
              value={input}
              onChange={handleInputChange}
              placeholder={placeholder}
              rows="4"
              spellCheck="false"
            />
          ) : (
            <input
              type="text"
              className={`smart-input ${!isValid ? 'error' : ''}`}
              value={input}
              onChange={handleInputChange}
              placeholder={placeholder}
              spellCheck="false"
            />
          )}
          
          {/* Indicateur de validation */}
          <div className="input-status">
            {input && (
              <span className={`status-icon ${isValid ? 'valid' : 'invalid'}`}>
                <i className={isValid ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'}></i>
              </span>
            )}
          </div>
        </div>

        {/* Message d'erreur */}
        {errorMessage && (
          <div className="error-message">
            <i className="fas fa-exclamation-triangle"></i>
            {errorMessage}
          </div>
        )}

        {/* Exemples */}
        <div className="input-examples">
          <span className="examples-label">Exemples :</span>
          {getExamples().map((example, index) => (
            <button
              key={index}
              type="button"
              className="example-btn"
              onClick={() => loadExample(example)}
            >
              {example}
            </button>
          ))}
        </div>

        {/* Bouton d'action */}
        <div className="input-actions">
          <button 
            type="submit" 
            className="btn btn-primary analyze-btn"
            disabled={!isValid || !input.trim()}
          >
            <i className="fas fa-search"></i>
            Analyser le contenu
          </button>
          
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={() => {
              setInput('');
              setIsValid(true);
              setErrorMessage('');
            }}
          >
            <i className="fas fa-times"></i>
            Effacer
          </button>
        </div>
      </form>

     
    </div>
  );
};

export default SmartInputBar;