import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Login from './Login';
import './AdminToggle.css';

const AdminToggle = ({ children }) => {
  const { isAuthenticated, logout, isLoading } = useAuth();
  const [showLogin, setShowLogin] = useState(false);

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (showLogin && !isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="admin-toggle-container">
      <div className="admin-header">
        <div className="mode-indicator">
          <span className={`mode-badge ${isAuthenticated ? 'admin' : 'restricted'}`}>
            {isAuthenticated ? '🔓 Admin Mode' : '👁️ Restricted Mode'}
          </span>
        </div>
        
        <div className="admin-controls">
          {!isAuthenticated ? (
            <button 
              onClick={() => setShowLogin(true)}
              className="auth-button admin-login"
            >
              Switch to Admin Mode
            </button>
          ) : (
            <button 
              onClick={logout}
              className="auth-button logout"
            >
              Logout (Switch to Restricted)
            </button>
          )}
        </div>
      </div>
      
      <div className="content-container">
        {children}
      </div>
    </div>
  );
};

export default AdminToggle;