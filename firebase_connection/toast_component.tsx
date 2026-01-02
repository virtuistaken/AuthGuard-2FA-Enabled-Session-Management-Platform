import React, { useState, useEffect } from 'react';

/**
 * Toast Notification Component
 * HAFTA 5 - Sprint 5 Implementation
 * 
 * Usage:
 *   const { showToast, ToastContainer } = useToast();
 *   showToast('Success!', 'success');
 *   return <div>{ToastContainer}</div>
 */

export const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const showToast = (message, type = 'info', duration = 3000) => {
    const id = Date.now();
    const newToast = { id, message, type, duration };
    
    setToasts(prev => [...prev, newToast]);

    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, duration);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const ToastContainer = (
    <div style={{
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    }}>
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );

  return { showToast, ToastContainer };
};

const Toast = ({ message, type, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setTimeout(() => setIsVisible(true), 10);
  }, []);

  const getBackgroundColor = () => {
    switch (type) {
      case 'success': return '#d4edda';
      case 'error': return '#f8d7da';
      case 'warning': return '#fff3cd';
      case 'info': return '#d1ecf1';
      default: return '#f8f9fa';
    }
  };

  const getBorderColor = () => {
    switch (type) {
      case 'success': return '#c3e6cb';
      case 'error': return '#f5c6cb';
      case 'warning': return '#ffeaa7';
      case 'info': return '#bee5eb';
      default: return '#dee2e6';
    }
  };

  const getTextColor = () => {
    switch (type) {
      case 'success': return '#155724';
      case 'error': return '#721c24';
      case 'warning': return '#856404';
      case 'info': return '#0c5460';
      default: return '#383d41';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📝';
    }
  };

  return (
    <div style={{
      background: getBackgroundColor(),
      border: `1px solid ${getBorderColor()}`,
      borderRadius: '8px',
      padding: '12px 16px',
      minWidth: '300px',
      maxWidth: '400px',
      color: getTextColor(),
      fontSize: '14px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      opacity: isVisible ? 1 : 0,
      transform: isVisible ? 'translateX(0)' : 'translateX(20px)',
      transition: 'all 0.3s ease',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <span style={{ fontSize: '20px' }}>{getIcon()}</span>
      <span style={{ flex: 1 }}>{message}</span>
      <button
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          color: getTextColor(),
          cursor: 'pointer',
          fontSize: '18px',
          padding: '0',
          lineHeight: '1'
        }}
      >
        ×
      </button>
    </div>
  );
};

// Demo Component
export const ToastDemo = () => {
  const { showToast, ToastContainer } = useToast();

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    }}>
      {ToastContainer}
      
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2rem',
        boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
      }}>
        <h2 style={{ margin: '0 0 1.5rem', textAlign: 'center' }}>
          🍞 Toast Notifications
        </h2>
        
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <button
            onClick={() => showToast('Operation completed successfully!', 'success')}
            style={{
              padding: '12px 24px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Show Success
          </button>
          
          <button
            onClick={() => showToast('Something went wrong!', 'error')}
            style={{
              padding: '12px 24px',
              background: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Show Error
          </button>
          
          <button
            onClick={() => showToast('Please be careful!', 'warning')}
            style={{
              padding: '12px 24px',
              background: '#ffc107',
              color: '#333',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Show Warning
          </button>
          
          <button
            onClick={() => showToast('Here is some information', 'info')}
            style={{
              padding: '12px 24px',
              background: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Show Info
          </button>
        </div>
      </div>
    </div>
  );
};

export default useToast;
