import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const [securityCode, setSecurityCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!securityCode.trim()) {
      setError('Please enter security code');
      setIsLoading(false);
      return;
    }

    const result = await login(securityCode);
    
    if (!result.success) {
      setError(result.error);
      setSecurityCode('');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>🔒 Admin Access</h2>
          <p>Enter security code to access admin features</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="securityCode">Security Code:</label>
            <input
              type="password"
              id="securityCode"
              value={securityCode}
              onChange={(e) => setSecurityCode(e.target.value)}
              placeholder="Enter your security code"
              disabled={isLoading}
              autoFocus
            />
          </div>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? 'Authenticating...' : 'Login'}
          </button>
        </form>
        
        <div className="login-info">
          <p><strong>Restricted Mode Features:</strong></p>
          <ul>
            <li>✅ View documents</li>
            <li>✅ Search by tag</li>
            <li>✅ Download data</li>
          </ul>
          
          <p><strong>Admin Mode Features:</strong></p>
          <ul>
            <li>✅ All restricted features</li>
            <li>✅ Upload new documents</li>
            <li>✅ Edit documents</li>
            <li>✅ Delete documents</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;