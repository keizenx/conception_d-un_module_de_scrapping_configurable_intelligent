/* =========================================
 * frontend/src/services/api.js
 * Service pour toutes les requêtes API vers le backend Django
 * Centralise tous les appels HTTP
 * RELEVANT FILES: AuthContext.jsx, Dashboard.jsx, Analysis.jsx
 * ========================================= */

const API_BASE_URL = 'http://localhost:8000/api';

class APIService {
  // Headers communs pour toutes les requêtes
  getHeaders() {
    const token = localStorage.getItem('scraper_pro_token');
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }
    
    return headers;
  }

  // Gestion des erreurs
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Une erreur est survenue' }));
      throw new Error(error.detail || error.message || 'Erreur serveur');
    }
    return response.json();
  }

  // ==================== AUTH ====================
  
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    const data = await this.handleResponse(response);
    
    // Stocker le token
    if (data.token) {
      localStorage.setItem('scraper_pro_token', data.token);
    }
    
    return data;
  }

  async register(name, email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        username: email.split('@')[0], // Utiliser la partie avant @ comme username
        email, 
        password,
        password_confirm: password,
        first_name: name.split(' ')[0] || name,
        last_name: name.split(' ').slice(1).join(' ') || ''
      }),
    });
    
    const data = await this.handleResponse(response);
    
    // Stocker le token
    if (data.token) {
      localStorage.setItem('scraper_pro_token', data.token);
    }
    
    return data;
  }

  async logout() {
    try {
      await fetch(`${API_BASE_URL}/auth/logout/`, {
        method: 'POST',
        headers: this.getHeaders(),
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('scraper_pro_token');
      localStorage.removeItem('scraper_pro_user');
    }
  }

  async getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/auth/me/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  // ==================== DASHBOARD ====================
  
  async getDashboardStats() {
    const response = await fetch(`${API_BASE_URL}/dashboard/stats/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }
  
  async getRecentSessions() {
    const response = await fetch(`${API_BASE_URL}/dashboard/recent_sessions/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }
  
  async getActivityData() {
    const response = await fetch(`${API_BASE_URL}/dashboard/activity/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  // ==================== ANALYSIS ====================
  
  async quickAnalyze(url) {
    // Analyse rapide sans authentification (pour landing page)
    const response = await fetch(`${API_BASE_URL}/analysis/quick_analyze/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    
    return this.handleResponse(response);
  }
  
  async analyzeURL(url, includeSubdomains = false) {
    const response = await fetch(`${API_BASE_URL}/analysis/analyze/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ 
        url, 
        include_subdomains: includeSubdomains 
      }),
    });
    
    return this.handleResponse(response);
  }

  async getAnalysisResults(analysisId) {
    const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  // ==================== SCRAPING ====================
  
  async getLatestSession() {
    const response = await fetch(`${API_BASE_URL}/scraping/latest/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }
  
  async startScraping(config) {
    const response = await fetch(`${API_BASE_URL}/scraping/start/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        url: config.url,
        content_types: config.selectedTypes,
        depth: config.depth,
        delay: config.delay,
        user_agent: config.userAgent,
        timeout: config.timeout,
        custom_selectors: config.customSelectors,
        export_format: config.format,
      }),
    });
    
    return this.handleResponse(response);
  }

  async getScrapingStatus(sessionId) {
    const response = await fetch(`${API_BASE_URL}/scraping/${sessionId}/status/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async getSessionLogs(sessionId) {
    const response = await fetch(`${API_BASE_URL}/scraping/${sessionId}/logs/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async getSessionResults(sessionId) {
    const response = await fetch(`${API_BASE_URL}/scraping/${sessionId}/results/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async stopScraping(sessionId) {
    const response = await fetch(`${API_BASE_URL}/scraping/${sessionId}/stop/`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async rescrape(sessionId) {
    const response = await fetch(`${API_BASE_URL}/scraping/${sessionId}/rescrape/`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  // ==================== RESULTS ====================
  
  async getResults(sessionId, filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.search) params.append('search', filters.search);
    if (filters.category) params.append('category', filters.category);
    if (filters.stock) params.append('stock', filters.stock);
    if (filters.page) params.append('page', filters.page);
    
    const response = await fetch(
      `${API_BASE_URL}/results/${sessionId}/?${params.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );
    
    return this.handleResponse(response);
  }

  async exportResults(sessionId, format, options = {}) {
    // Note: 'format' est réservé par DRF, on utilise 'type'
    // Pour ZIP_IMAGES, le téléchargement peut être long (images à télécharger côté serveur)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), format === 'zip_images' ? 300000 : 60000); // 5min pour images, 1min sinon
    
    try {
      // Construire les paramètres de requête
      const params = new URLSearchParams({ type: format });
      
      // Ajouter la limite si spécifiée
      if (options.limit && options.limit > 0) {
        params.append('limit', options.limit);
      }
      
      // Ajouter les IDs si spécifiés
      if (options.item_ids && Array.isArray(options.item_ids) && options.item_ids.length > 0) {
        params.append('item_ids', options.item_ids.join(','));
      }
      
      const response = await fetch(
        `${API_BASE_URL}/results/${sessionId}/export/?${params.toString()}`,
        {
          method: 'GET',
          headers: this.getHeaders(),
          signal: controller.signal,
        }
      );
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error('Erreur lors de l\'export');
      }
      
      // Retourner le blob (le téléchargement est géré par le composant appelant)
      return await response.blob();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Le téléchargement a pris trop de temps. Réessayez.');
      }
      throw error;
    }
  }

  // ==================== REPORTS ====================
  
  async getReports(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.period) params.append('period', filters.period);
    if (filters.page) params.append('page', filters.page);
    
    const response = await fetch(
      `${API_BASE_URL}/reports/?${params.toString()}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );
    
    return this.handleResponse(response);
  }

  async getReport(reportId) {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async downloadReport(reportId, format) {
    const response = await fetch(
      `${API_BASE_URL}/reports/${reportId}/download/?format=${format}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );
    
    if (!response.ok) {
      throw new Error('Erreur lors du téléchargement');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${reportId}.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  // ==================== DASHBOARD ====================
  
  async getDashboardStats() {
    const response = await fetch(`${API_BASE_URL}/dashboard/stats/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async getRecentSessions() {
    // Note: la route DRF utilise underscore, pas slash
    const response = await fetch(`${API_BASE_URL}/dashboard/recent_sessions/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async getActivityData() {
    const response = await fetch(`${API_BASE_URL}/dashboard/activity/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  // ==================== API KEYS ====================
  
  async getApiKeys() {
    const response = await fetch(`${API_BASE_URL}/settings/api-keys/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async createApiKey(data) {
    const response = await fetch(`${API_BASE_URL}/settings/api-keys/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    
    return this.handleResponse(response);
  }

  async deleteApiKey(keyId) {
    const response = await fetch(`${API_BASE_URL}/settings/api-keys/${keyId}/`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Erreur suppression clé');
    }
    
    return { success: true };
  }

  // ==================== WEBHOOKS ====================
  
  async getWebhooks() {
    const response = await fetch(`${API_BASE_URL}/settings/webhooks/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async createWebhook(data) {
    const response = await fetch(`${API_BASE_URL}/settings/webhooks/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    
    return this.handleResponse(response);
  }

  async deleteWebhook(webhookId) {
    const response = await fetch(`${API_BASE_URL}/settings/webhooks/${webhookId}/`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error('Erreur suppression webhook');
    }
    
    return { success: true };
  }
}

// Export une instance unique
export default new APIService();
