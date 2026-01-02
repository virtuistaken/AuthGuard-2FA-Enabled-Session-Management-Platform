import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

/**
 * Login Page Component
 * HAFTA 5 - Sprint 5 Implementation
 * 
 * Features:
 * - Email/Password login
 * - Conditional 2FA input (if required)
 * - Form validation
 * - Error handling
 * - Loading states
 */
export const LoginPage = () => {
  const { login, verify2FA, requires2FA, loading } = useAuth();
  
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  
  // UI state
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Validation
  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side validation
    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(email, password);
      
      if (result.requires2fa) {
        // 2FA required - input will appear
        setError('');
      } else if (result.success) {
        // Success - redirect will happen via AuthContext
        window.location.href = '/dashboard';
      } else {
        setError(result.message || 'Login failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handle2FAVerify = async (e) => {
    e.preventDefault();
    setError('');

    if (totpCode.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }

    setIsLoading(true);

    try {
      const result = await verify2FA(totpCode);
      
      if (result.success) {
        window.location.href = '/dashboard';
      } else {
        setError(result.message || '2FA verification failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        padding: '3rem',
        width: '100%',
        maxWidth: '400px'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '48px', marginBottom: '0.5rem' }}>🔐</div>
          <h1 style={{ margin: 0, fontSize: '28px', color: '#333' }}>
            {requires2FA ? '2FA Verification' : 'Welcome Back'}
          </h1>
          <p style={{ margin: '0.5rem 0 0', color: '#666', fontSize: '14px' }}>
            {requires2FA ? 'Enter your 6-digit code' : 'Sign in to your account'}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            background: '#fee',
            border: '1px solid #fcc',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '1.5rem',
            color: '#c33',
            fontSize: '14px'
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Login Form */}
        {!requires2FA ? (
          <form onSubmit={handleLogin}>
            {/* Email Input */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '500',
                color: '#333',
                fontSize: '14px'
              }}>
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '16px',
                  transition: 'border-color 0.2s',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                required
              />
            </div>

            {/* Password Input */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '500',
                color: '#333',
                fontSize: '14px'
              }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  style={{
                    width: '100%',
                    padding: '12px',
                    paddingRight: '48px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px',
                    fontSize: '16px',
                    transition: 'border-color 0.2s',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '20px'
                  }}
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '14px',
                background: isLoading ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'transform 0.2s',
                marginTop: '0.5rem'
              }}
              onMouseEnter={(e) => !isLoading && (e.target.style.transform = 'scale(1.02)')}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              {isLoading ? '🔄 Signing in...' : '🚀 Sign In'}
            </button>
          </form>
        ) : (
          /* 2FA Form */
          <form onSubmit={handle2FAVerify}>
            {/* TOTP Code Input */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '500',
                color: '#333',
                fontSize: '14px'
              }}>
                Authentication Code
              </label>
              <input
                type="text"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                maxLength={6}
                style={{
                  width: '100%',
                  padding: '16px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '24px',
                  textAlign: 'center',
                  letterSpacing: '8px',
                  fontWeight: '600',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                autoFocus
                required
              />
              <p style={{
                margin: '0.5rem 0 0',
                fontSize: '12px',
                color: '#666',
                textAlign: 'center'
              }}>
                Enter the 6-digit code from your authenticator app
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '14px',
                background: isLoading ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'transform 0.2s'
              }}
              onMouseEnter={(e) => !isLoading && (e.target.style.transform = 'scale(1.02)')}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              {isLoading ? '🔄 Verifying...' : '✅ Verify Code'}
            </button>
          </form>
        )}

        {/* Register Link */}
        <div style={{
          marginTop: '2rem',
          textAlign: 'center',
          fontSize: '14px',
          color: '#666'
        }}>
          Don't have an account?{' '}
          <a
            href="/register"
            style={{
              color: '#667eea',
              textDecoration: 'none',
              fontWeight: '600'
            }}
            onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
            onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
          >
            Sign up
          </a>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
