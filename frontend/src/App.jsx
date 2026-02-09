import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ScrapingProvider } from './contexts/ScrapingContext';
import { ThemeProvider } from './contexts/ThemeContext';
import NotificationCenter from './components/NotificationCenter/NotificationCenter';
import Landing from './pages/Landing/Landing';
import Login from './pages/Login/Login';
import ForgotPassword from './pages/Login/ForgotPassword';
import ResetPassword from './pages/Login/ResetPassword';
import Register from './pages/Register/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import Analysis from './pages/Analysis/Analysis';
import Results from './pages/Results/Results';
import Reports from './pages/Reports/Reports';
import Settings from './pages/Settings/Settings';
import Profile from './pages/Profile/Profile';
import Layout from './components/Layout/Layout';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Chargement...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <ScrapingProvider>
          <BrowserRouter>
            <AppContent />
          </BrowserRouter>
        </ScrapingProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

// Composant séparé pour avoir accès au BrowserRouter
function AppContent() {
  return (
    <>
      <NotificationCenter />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<ProtectedRoute><Layout title="Dashboard"><Dashboard /></Layout></ProtectedRoute>} />
        <Route path="/analysis" element={<ProtectedRoute><Layout title="Nouvelle Analyse"><Analysis /></Layout></ProtectedRoute>} />
        <Route path="/results" element={<ProtectedRoute><Layout title="Résultats"><Results /></Layout></ProtectedRoute>} />
        <Route path="/reports" element={<ProtectedRoute><Layout title="Rapports"><Reports /></Layout></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Layout title="Paramètres"><Settings /></Layout></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Layout title="Mon Profil"><Profile /></Layout></ProtectedRoute>} />
      </Routes>
    </>
  );
}

export default App;
