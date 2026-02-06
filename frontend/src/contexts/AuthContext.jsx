/* =========================================
 * frontend/src/contexts/AuthContext.jsx
 * Gère l'état d'authentification de l'application
 * Connecté au backend Django pour l'authentification
 * RELEVANT FILES: App.jsx, Login.jsx, Register.jsx, services/api.js
 * ========================================= */

import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Vérifier si un token existe au démarrage
    const token = localStorage.getItem('scraper_pro_token');
    if (token) {
      // Récupérer les infos utilisateur depuis l'API
      api.getUserProfile()
        .then(userData => {
          // On mappe avatar_url -> avatar pour uniformiser partout
          const mappedUser = {
            ...userData,
            avatar: userData.avatar_url || null
          };
          setUser(mappedUser);
          localStorage.setItem('scraper_pro_user', JSON.stringify(mappedUser));
        })
        .catch(error => {
          console.error('Erreur lors de la récupération de l\'utilisateur:', error);
          localStorage.removeItem('scraper_pro_token');
          localStorage.removeItem('scraper_pro_user');
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const data = await api.login(email, password);
      
      // Si 2FA requis, on renvoie l'info sans connecter l'user
      if (data['2fa_required']) {
        return { success: true, requires2FA: true, message: data.message };
      }

      const userData = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role || 'user',
        avatar: data.user.avatar_url || null
      };
      setUser(userData);
      localStorage.setItem('scraper_pro_user', JSON.stringify(userData));
      return { success: true, user: userData };
    } catch (error) {
      return { success: false, error: error.message || 'Email ou mot de passe incorrect' };
    }
  };

  const verify2FA = async (email, password, code) => {
    try {
      const data = await api.verify2FA(email, password, code);
      
      const userData = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role || 'user',
        avatar: data.user.avatar_url || null
      };
      setUser(userData);
      localStorage.setItem('scraper_pro_user', JSON.stringify(userData));
      return { success: true, user: userData };
    } catch (error) {
      return { success: false, error: error.message || 'Code incorrect' };
    }
  };

  const verifyEmail = async (email, code) => {
    try {
      const data = await api.verifyEmail(email, code);
      
      const userData = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role || 'user',
        avatar: data.user.avatar_url || null
      };
      setUser(userData);
      localStorage.setItem('scraper_pro_user', JSON.stringify(userData));
      return { success: true, user: userData };
    } catch (error) {
      return { success: false, error: error.message || 'Code incorrect' };
    }
  };

  const register = async (name, email, password) => {
    try {
      const data = await api.register(name, email, password);
      
      if (data.verification_required) {
        return { success: true, verificationRequired: true, message: data.message };
      }

      const userData = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        role: data.user.role || 'user',
        avatar: data.user.avatar_url || null
      };
      setUser(userData);
      localStorage.setItem('scraper_pro_user', JSON.stringify(userData));
      return { success: true, user: userData };
    } catch (error) {
      return { success: false, error: error.message || 'Erreur lors de l\'inscription' };
    }
  };

  const logout = async () => {
    await api.logout();
    setUser(null);
  };

  const updateUser = (updatedData) => {
    const updatedUser = { ...user, ...updatedData };
    setUser(updatedUser);
    localStorage.setItem('scraper_pro_user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    verify2FA,
    verifyEmail,
    register,
    logout,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};

export default AuthContext;
