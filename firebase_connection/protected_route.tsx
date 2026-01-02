import React from 'react';
import { useAuth } from './AuthContext';

/**
 * Protected Route Component
 * HAFTA 4 - Sprint 4 Implementation
 * 
 * Token kontrolü yapar:
 * - Token varsa: children'ı render et
 * - Token yoksa: Login sayfasına yönlendir
 */
export const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  // Loading state
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '4px solid #f3f3f3',
            borderTop: '4px solid #3498db',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }}></div>
          <p style={{ color: '#666' }}>Loading...</p>
        </div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Authenticated - render children
  if (user) {
    return <>{children}</>;
  }

  // Not authenticated - show login message
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div style={{
        background: 'white',
        padding: '3rem',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        textAlign: 'center',
        maxWidth: '400px'
      }}>
        <div style={{
          fontSize: '64px',
          marginBottom: '1rem'
        }}>🔒</div>
        <h2 style={{
          margin: '0 0 0.5rem',
          color: '#333',
          fontSize: '24px'
        }}>Authentication Required</h2>
        <p style={{
          color: '#666',
          marginBottom: '2rem',
          fontSize: '14px'
        }}>Please login to access this page</p>
        <button
          onClick={() => window.location.href = '/login'}
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            padding: '12px 32px',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'transform 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
        >
          Go to Login
        </button>
      </div>
    </div>
  );
};

export default ProtectedRoute;
