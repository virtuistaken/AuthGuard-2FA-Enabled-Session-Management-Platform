import React, { createContext, useState, useContext, useEffect } from 'react';

// API Base URL
const API_URL = 'http://localhost:8000';

// Fetch helper function
const apiRequest = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_URL}${endpoint}`, config);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }

  return data;
};

// Auth Context
const AuthContext = createContext(null);

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requires2FA, setRequires2FA] = useState(false);
  const [pendingEmail, setPendingEmail] = useState(null);

  // Token'ı localStorage'dan kontrol et
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  // Current user bilgisini getir
  const fetchCurrentUser = async (token) => {
    try {
      const data = await apiRequest('/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  // Register
  const register = async (username, email, password) => {
    try {
      const data = await apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      });
      return { success: true, message: data.message };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Registration failed',
      };
    }
  };

  // Login
  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      // Case 1: 2FA Required (HTTP 202 or requires_2fa flag)
      if (data.requires_2fa) {
        setRequires2FA(true);
        setPendingEmail(email);
        return {
          success: false,
          requires2fa: true,
          message: data.message,
        };
      }

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Case 2: Success - Save tokens
      const { access_token, refresh_token } = data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      await fetchCurrentUser(access_token);

      return { success: true, message: 'Login successful' };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Login failed',
      };
    }
  };

  // Verify 2FA
  const verify2FA = async (token) => {
    try {
      const data = await apiRequest('/auth/verify-2fa', {
        method: 'POST',
        body: JSON.stringify({
          email: pendingEmail,
          token,
        }),
      });

      const { access_token, refresh_token } = data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      setRequires2FA(false);
      setPendingEmail(null);

      await fetchCurrentUser(access_token);

      return { success: true, message: 'Login successful with 2FA' };
    } catch (error) {
      return {
        success: false,
        message: error.message || '2FA verification failed',
      };
    }
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setRequires2FA(false);
    setPendingEmail(null);
  };

  // Enable 2FA
  const enable2FA = async (email) => {
    try {
      const data = await apiRequest('/2fa/enable', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
      return {
        success: true,
        qrCode: data.qr_code,
        secret: data.secret,
      };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Failed to enable 2FA',
      };
    }
  };

  // Disable 2FA
  const disable2FA = async (email) => {
    try {
      await apiRequest('/2fa/disable', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
      return { success: true };
    } catch (error) {
      return { success: false };
    }
  };

  // Get 2FA Status
  const get2FAStatus = async (email) => {
    try {
      const data = await apiRequest(`/2fa/status?email=${email}`);
      return data;
    } catch (error) {
      return null;
    }
  };

  const value = {
    user,
    loading,
    requires2FA,
    pendingEmail,
    register,
    login,
    verify2FA,
    logout,
    enable2FA,
    disable2FA,
    get2FAStatus,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default AuthContext;
