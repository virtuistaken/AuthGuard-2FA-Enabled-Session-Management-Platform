import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

/**
 * Dashboard Component
 * HAFTA 5 - Sprint 5 Implementation
 * 
 * Features:
 * - User info display
 * - 2FA management (enable/disable)
 * - QR code display
 * - 2FA testing
 */
export const Dashboard = () => {
  const { user, logout, enable2FA, disable2FA, get2FAStatus } = useAuth();
  
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [showQR, setShowQR] = useState(false);
  const [testCode, setTestCode] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadUser2FAStatus();
  }, []);

  const loadUser2FAStatus = async () => {
    if (user?.email) {
      const status = await get2FAStatus(user.email);
      if (status) {
        setIs2FAEnabled(status.is_enabled);
      }
    }
  };

  const handleEnable2FA = async () => {
    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await enable2FA(user.email);
      
      if (result.success) {
        setQrCode(result.qrCode);
        setSecret(result.secret);
        setShowQR(true);
        setMessage({
          type: 'success',
          text: '2FA enabled! Scan the QR code with your authenticator app'
        });
        setIs2FAEnabled(true);
      } else {
        setMessage({
          type: 'error',
          text: result.message || 'Failed to enable 2FA'
        });
      }
    } catch (err) {
      setMessage({
        type: 'error',
        text: 'An unexpected error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!window.confirm('Are you sure you want to disable 2FA? This will make your account less secure.')) {
      return;
    }

    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await disable2FA(user.email);
      
      if (result.success) {
        setIs2FAEnabled(false);
        setShowQR(false);
        setMessage({
          type: 'success',
          text: '2FA disabled successfully'
        });
      } else {
        setMessage({
          type: 'error',
          text: 'Failed to disable 2FA'
        });
      }
    } catch (err) {
      setMessage({
        type: 'error',
        text: 'An unexpected error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '20px 0'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          marginBottom: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '28px', color: '#333' }}>
              🎯 Dashboard
            </h1>
            <p style={{ margin: '0.5rem 0 0', color: '#666' }}>
              Welcome, {user?.email || 'User'}!
            </p>
          </div>
          <button
            onClick={logout}
            style={{
              padding: '10px 24px',
              background: '#ff4757',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            🚪 Logout
          </button>
        </div>

        {/* Message */}
        {message.text && (
          <div style={{
            background: message.type === 'success' ? '#d4edda' : '#f8d7da',
            border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '20px',
            color: message.type === 'success' ? '#155724' : '#721c24',
            maxWidth: '1200px',
            margin: '0 auto 20px'
          }}>
            {message.type === 'success' ? '✅' : '⚠️'} {message.text}
          </div>
        )}

        {/* Security Settings Card */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ margin: '0 0 1rem', fontSize: '24px', color: '#333' }}>
            🔐 Security Settings
          </h2>
          
          <div style={{
            background: '#f8f9fa',
            borderRadius: '12px',
            padding: '1.5rem',
            marginBottom: '1.5rem'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '18px', color: '#333' }}>
                  Two-Factor Authentication
                </h3>
                <p style={{ margin: '0.5rem 0 0', color: '#666', fontSize: '14px' }}>
                  Add an extra layer of security to your account
                </p>
              </div>
              <div style={{
                padding: '8px 16px',
                borderRadius: '20px',
                background: is2FAEnabled ? '#d4edda' : '#f8d7da',
                color: is2FAEnabled ? '#155724' : '#721c24',
                fontWeight: '600',
                fontSize: '14px'
              }}>
                {is2FAEnabled ? '✅ Enabled' : '❌ Disabled'}
              </div>
            </div>

            {!is2FAEnabled ? (
              <button
                onClick={handleEnable2FA}
                disabled={isLoading}
                style={{
                  padding: '12px 24px',
                  background: isLoading ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: isLoading ? 'not-allowed' : 'pointer'
                }}
              >
                {isLoading ? '⏳ Enabling...' : '🔒 Enable 2FA'}
              </button>
            ) : (
              <button
                onClick={handleDisable2FA}
                disabled={isLoading}
                style={{
                  padding: '12px 24px',
                  background: isLoading ? '#ccc' : '#ff4757',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: isLoading ? 'not-allowed' : 'pointer'
                }}
              >
                {isLoading ? '⏳ Disabling...' : '🔓 Disable 2FA'}
              </button>
            )}
          </div>

          {/* QR Code Display */}
          {showQR && qrCode && (
            <div style={{
              background: '#fff',
              border: '2px solid #667eea',
              borderRadius: '12px',
              padding: '2rem',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 1rem', fontSize: '20px', color: '#333' }}>
                📱 Scan QR Code
              </h3>
              <p style={{ color: '#666', marginBottom: '1.5rem', fontSize: '14px' }}>
                Use Google Authenticator, Microsoft Authenticator, or any TOTP app
              </p>

              <div style={{
                display: 'inline-block',
                padding: '1rem',
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}>
                <img
                  src={qrCode}
                  alt="2FA QR Code"
                  style={{
                    width: '256px',
                    height: '256px',
                    display: 'block'
                  }}
                />
              </div>

              <div style={{
                marginTop: '1.5rem',
                padding: '1rem',
                background: '#f8f9fa',
                borderRadius: '8px'
              }}>
                <p style={{
                  margin: '0 0 0.5rem',
                  fontSize: '12px',
                  color: '#666',
                  fontWeight: '600'
                }}>
                  Manual Entry Key:
                </p>
                <code style={{
                  display: 'inline-block',
                  padding: '8px 16px',
                  background: '#fff',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontFamily: 'monospace',
                  color: '#333',
                  letterSpacing: '2px'
                }}>
                  {secret}
                </code>
              </div>

              <div style={{
                marginTop: '1.5rem',
                padding: '1rem',
                background: '#fff3cd',
                borderRadius: '8px',
                border: '1px solid #ffc107'
              }}>
                <p style={{ margin: 0, fontSize: '13px', color: '#856404' }}>
                  ⚠️ <strong>Important:</strong> Save this secret key in a safe place. 
                  You'll need it if you lose access to your authenticator app.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Account Info Card */}
        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '2rem',
          marginTop: '20px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ margin: '0 0 1rem', fontSize: '24px', color: '#333' }}>
            👤 Account Information
          </h2>
          <div style={{ color: '#666' }}>
            <p style={{ margin: '0.5rem 0' }}>
              <strong>User ID:</strong> {user?.user_id || 'N/A'}
            </p>
            <p style={{ margin: '0.5rem 0' }}>
              <strong>Email:</strong> {user?.email || 'N/A'}
            </p>
            <p style={{ margin: '0.5rem 0' }}>
              <strong>2FA Status:</strong>{' '}
              <span style={{
                color: is2FAEnabled ? '#28a745' : '#dc3545',
                fontWeight: '600'
              }}>
                {is2FAEnabled ? 'Protected ✅' : 'Not Protected ❌'}
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
