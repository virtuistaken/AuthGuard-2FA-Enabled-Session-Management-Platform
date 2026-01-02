import React, { useState } from 'react';
import { useAuth } from './AuthContext';

/**
 * Login Component
 * HAFTA 5 - Sprint 5 Implementation
 */
export const Login = () => {
  const { login, verify2FA, requires2FA } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleLogin = async () => {
    setError('');

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
        setError('');
      } else if (result.success) {
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

  const handle2FAVerify = async () => {
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
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        padding: '3rem',
        width: '100%',
        maxWidth: '400px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ fontSize: '48px', marginBottom: '0.5rem' }}>🔐</div>
          <h1 style={{ margin: 0, fontSize: '28px', color: '#333' }}>
            {requires2FA ? '2FA Verification' : 'Welcome Back'}
          </h1>
          <p style={{ margin: '0.5rem 0 0', color: '#666', fontSize: '14px' }}>
            {requires2FA ? 'Enter your 6-digit code' : 'Sign in to your account'}
          </p>
        </div>

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

        {!requires2FA ? (
          <div>
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
                onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                placeholder="you@example.com"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '16px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

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
                  onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
                  placeholder="Enter your password"
                  style={{
                    width: '100%',
                    padding: '12px',
                    paddingRight: '48px',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px',
                    fontSize: '16px',
                    boxSizing: 'border-box'
                  }}
                />
                <button
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

            <button
              onClick={handleLogin}
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
                marginTop: '0.5rem'
              }}
            >
              {isLoading ? '🔄 Signing in...' : '🚀 Sign In'}
            </button>
          </div>
        ) : (
          <div>
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
                onKeyPress={(e) => e.key === 'Enter' && handle2FAVerify()}
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
                autoFocus
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

            <button
              onClick={handle2FAVerify}
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
                cursor: isLoading ? 'not-allowed' : 'pointer'
              }}
            >
              {isLoading ? '🔄 Verifying...' : '✅ Verify Code'}
            </button>
          </div>
        )}

        <div style={{
          marginTop: '2rem',
          textAlign: 'center',
          fontSize: '14px',
          color: '#666'
        }}>
          Don't have an account?{' '}
          <span
            onClick={() => window.location.href = '/register'}
            style={{
              color: '#667eea',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Sign up
          </span>
        </div>
      </div>
    </div>
  );
};

export default Login;
