import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

// API Base URL
const API_URL = 'http://localhost:8000';

// Axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth Context
const AuthContext = createContext(null);

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requires2FA, setRequires2FA] = useState(false);
  const [pendingEmail, setPendingEmail] = useState(null);

  // Token'ı localStorage'dan al
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Token varsa user bilgisini al
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  // Axios interceptor - Her request'e token ekle
  useEffect(() => {
    const interceptor = api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => api.interceptors.request.eject(interceptor);
  }, []);

  // Current user bilgisini getir
  const fetchCurrentUser = async (token) => {
    try {
      const response = await api.get('/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data);
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
      const response = await api.post('/auth/register', {
        username,
        email,
        password,
      });
      return { success: true, message: response.data.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  // Login
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      });

      // Case 1: 2FA Required (HTTP 202)
      if (response.data.requires_2fa) {
        setRequires2FA(true);
        setPendingEmail(email);
        return {
          success: false,
          requires2fa: true,
          message: response.data.message,
        };
      }

      // Case 2: Success - Save tokens
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // Fetch user data
      await fetchCurrentUser(access_token);

      return { success: true, message: 'Login successful' };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  // Verify 2FA
  const verify2FA = async (token) => {
    try {
      const response = await api.post('/auth/verify-2fa', {
        email: pendingEmail,
        token,
      });

      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      setRequires2FA(false);
      setPendingEmail(null);

      await fetchCurrentUser(access_token);

      return { success: true, message: 'Login successful with 2FA' };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '2FA verification failed',
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
      const response = await api.post('/2fa/enable', { email });
      return {
        success: true,
        qrCode: response.data.qr_code,
        secret: response.data.secret,
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to enable 2FA',
      };
    }
  };

  // Disable 2FA
  const disable2FA = async (email) => {
    try {
      await api.post('/2fa/disable', { email });
      return { success: true };
    } catch (error) {
      return { success: false };
    }
  };

  // Get 2FA Status
  const get2FAStatus = async (email) => {
    try {
      const response = await api.get(`/2fa/status?email=${email}`);
      return response.data;
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
