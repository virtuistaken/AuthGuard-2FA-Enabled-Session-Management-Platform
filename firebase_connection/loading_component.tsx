import React from 'react';

/**
 * Loading Spinner Component
 * HAFTA 5 - Sprint 5 Implementation
 */

export const LoadingSpinner = ({ size = 'medium', message = 'Loading...' }) => {
  const sizeMap = {
    small: '30px',
    medium: '50px',
    large: '70px'
  };

  const spinnerSize = sizeMap[size] || sizeMap.medium;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div
        style={{
          width: spinnerSize,
          height: spinnerSize,
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #667eea',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}
      />
      {message && (
        <p style={{
          marginTop: '1rem',
          color: '#666',
          fontSize: '14px',
          fontFamily: 'system-ui, -apple-system, sans-serif'
        }}>
          {message}
        </p>
      )}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export const LoadingOverlay = ({ message = 'Processing...' }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999
    }}>
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '2rem 3rem',
        boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
        textAlign: 'center'
      }}>
        <LoadingSpinner size="large" message={message} />
      </div>
    </div>
  );
};

export const LoadingButton = ({ onClick, isLoading, children, ...props }) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      {...props}
      style={{
        ...props.style,
        opacity: isLoading ? 0.7 : 1,
        cursor: isLoading ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px'
      }}
    >
      {isLoading && (
        <div
          style={{
            width: '16px',
            height: '16px',
            border: '2px solid transparent',
            borderTop: '2px solid white',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }}
        />
      )}
      {children}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </button>
  );
};

// Demo Component
export const LoadingDemo = () => {
  const [showOverlay, setShowOverlay] = React.useState(false);
  const [buttonLoading, setButtonLoading] = React.useState(false);

  const handleButtonClick = () => {
    setButtonLoading(true);
    setTimeout(() => setButtonLoading(false), 2000);
  };

  const handleOverlayClick = () => {
    setShowOverlay(true);
    setTimeout(() => setShowOverlay(false), 3000);
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
      {showOverlay && <LoadingOverlay message="Processing your request..." />}
      
      <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '3rem',
        boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
        maxWidth: '600px',
        width: '100%'
      }}>
        <h2 style={{ margin: '0 0 2rem', textAlign: 'center' }}>
          ⏳ Loading Components
        </h2>

        {/* Spinner Sizes */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '16px', color: '#333' }}>
            Spinner Sizes
          </h3>
          <div style={{
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            padding: '2rem',
            background: '#f8f9fa',
            borderRadius: '12px'
          }}>
            <LoadingSpinner size="small" message="Small" />
            <LoadingSpinner size="medium" message="Medium" />
            <LoadingSpinner size="large" message="Large" />
          </div>
        </div>

        {/* Loading Button */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ margin: '0 0 1rem', fontSize: '16px', color: '#333' }}>
            Loading Button
          </h3>
          <LoadingButton
            onClick={handleButtonClick}
            isLoading={buttonLoading}
            style={{
              width: '100%',
              padding: '14px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            {buttonLoading ? 'Loading...' : 'Click Me'}
          </LoadingButton>
        </div>

        {/* Loading Overlay */}
        <div>
          <h3 style={{ margin: '0 0 1rem', fontSize: '16px', color: '#333' }}>
            Loading Overlay
          </h3>
          <button
            onClick={handleOverlayClick}
            style={{
              width: '100%',
              padding: '14px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Show Overlay (3s)
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
