import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if there's a stored token on app load
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const login = async (securityCode) => {
    try {
      const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ security_code: securityCode }),
      });

      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        setIsAuthenticated(true);
        localStorage.setItem('auth_token', data.access_token);
        return { success: true };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || 'Authentication failed' };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('auth_token');
  };

  const getAuthHeaders = (includeContentType = true) => {
    const headers = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (includeContentType) {
      headers['Content-Type'] = 'application/json';
    }
    
    return headers;
  };

  const value = {
    isAuthenticated,
    token,
    isLoading,
    login,
    logout,
    getAuthHeaders,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};