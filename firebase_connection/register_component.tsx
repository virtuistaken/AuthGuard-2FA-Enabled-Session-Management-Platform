import React, { useState } from 'react';
import { useAuth } from './AuthContext';

/**
 * Register Component
 * HAFTA 5 - Sprint 5 Implementation
 */
export const Register = () => {
  const { register } = useAuth();
  
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePassword = (password) => {
    return password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password);
  };

  const handleRegister = async () => {
    setError('');

    // Validation
    if (username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    if (!validatePassword(password)) {
      setError('Password must be at least 8 characters with uppercase and number');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);

    try {
      const result = await register(username, email, password);
      
      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setError(result.message || 'Registration failed');
      }
    } catch (err) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
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
          textAlign: 'center',
          maxWidth: '400px'
        }}>
          <div style={{ fontSize: '64px', marginBottom: '1rem' }}>✅</div>
          <h2 style={{ margin: 0, color: '#333', fontSize: '24px' }}>
            Registration Successful!
          </h2>
          <p style={{ color: '#666', marginTop: '0.5rem' }}>
            Redirecting to login...
          </p>
        </div>
      </div>
    );
  }

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
          <div style={{ fontSize: '48px', marginBottom: '0.5rem' }}>🚀</div>
          <h1 style={{ margin: 0, fontSize: '28px', color: '#333' }}>
            Create Account
          </h1>
          <p style={{ margin: '0.5rem 0 0', color: '#666', fontSize: '14px' }}>
            Sign up to get started with AuthGuard
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

        {/* Username */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '500',
            color: '#333',
            fontSize: '14px'
          }}>
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="johndoe"
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

        {/* Email */}
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
              boxSizing: 'border-box'
            }}
          />
        </div>

        {/* Password */}
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
              placeholder="Min 8 chars, 1 uppercase, 1 number"
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
          {password && (
            <div style={{
              marginTop: '0.5rem',
              fontSize: '12px',
              color: validatePassword(password) ? '#2a7' : '#c33'
            }}>
              {validatePassword(password) ? '✅ Strong password' : '❌ Weak password'}
            </div>
          )}
        </div>

        {/* Confirm Password */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{
            display: 'block',
            marginBottom: '0.5rem',
            fontWeight: '500',
            color: '#333',
            fontSize: '14px'
          }}>
            Confirm Password
          </label>
          <input
            type={showPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleRegister()}
            placeholder="Re-enter your password"
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #e0e0e0',
              borderRadius: '8px',
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
          />
          {confirmPassword && (
            <div style={{
              marginTop: '0.5rem',
              fontSize: '12px',
              color: password === confirmPassword ? '#2a7' : '#c33'
            }}>
              {password === confirmPassword ? '✅ Passwords match' : '❌ Passwords do not match'}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          onClick={handleRegister}
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
          {isLoading ? '🔄 Creating Account...' : '🚀 Create Account'}
        </button>

        {/* Login Link */}
        <div style={{
          marginTop: '2rem',
          textAlign: 'center',
          fontSize: '14px',
          color: '#666'
        }}>
          Already have an account?{' '}
          <span
            onClick={() => window.location.href = '/login'}
            style={{
              color: '#667eea',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Sign in
          </span>
        </div>
      </div>
    </div>
  );
};

export default Register;
