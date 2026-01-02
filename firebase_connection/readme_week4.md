# 🔥 AuthGuard - HAFTA 4 Güncellemesi

AuthGuard: 2FA-Enabled Session Management Platform

## 🆕 Hafta 4 Yenilikleri

### ✅ Backend Yeni Modüller
- **jwt_manager.py** - JWT token yönetimi (Access + Refresh)
- **auth_service.py** - Login flow logic (conditional 2FA)
- **api_routes.py** - FastAPI endpoints (REST API)

### ✅ Frontend Temel Yapı
- **AuthContext.jsx** - Global auth state management
- **ProtectedRoute.jsx** - Route protection component

### ✅ Yeni Özellikler
- JWT Access Token (15 dakika)
- JWT Refresh Token (7 gün)
- Bcrypt password hashing
- Conditional login flow (2FA aware)
- FastAPI REST API
- CORS configuration
- Protected endpoints
- Token verification middleware

---

## 📦 Kurulum

### Backend Dependencies
```bash
pip install -r requirements_firebase.txt
```

**Yeni eklenen paketler (Hafta 4):**
- `python-jose==3.3.0` - JWT implementation
- `fastapi==0.104.1` - Modern web framework
- `uvicorn==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `bcrypt==4.1.2` - Password hashing

### Environment Variables
```bash
# .env dosyasına ekle
JWT_SECRET_KEY=your-secret-key-here-32-chars-min
ENCRYPTION_KEY=your-fernet-key-from-week2
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
```

---

## 🗂️ Güncel Dosya Yapısı

```
authguard_project/
│
├── backend/
│   ├── firebase_config.py           # Firebase bağlantısı
│   ├── data_schema.py               # Firestore şeması
│   ├── crud_operations.py           # Basit CRUD (Hafta 1)
│   │
│   ├── encryption.py                # Şifreleme (Hafta 2)
│   ├── md5_docid.py                 # MD5 doc_id (Hafta 2)
│   ├── secure_operations.py         # Şifreli işlemler (Hafta 2)
│   │
│   ├── totp_manager.py              # TOTP (Hafta 3)
│   ├── secure_2fa_operations.py     # 2FA ops (Hafta 3)
│   │
│   ├── jwt_manager.py               # 🆕 JWT (Hafta 4)
│   ├── auth_service.py              # 🆕 Auth logic (Hafta 4)
│   └── api_routes.py                # 🆕 FastAPI endpoints (Hafta 4)
│
└── frontend/
    ├── src/
    │   ├── contexts/
    │   │   └── AuthContext.jsx      # 🆕 Auth context (Hafta 4)
    │   └── components/
    │       └── ProtectedRoute.jsx   # 🆕 Route protection (Hafta 4)
    └── package.json
```

---

## 🔐 HAFTA 4: Session Management & JWT

### 1. JWT Manager

```python
from jwt_manager import JWTManager

jwt = JWTManager()

# Token pair oluştur
tokens = jwt.create_token_pair(user_id, email)
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer"
# }

# Access token doğrula
payload = jwt.verify_token(access_token, expected_type="access")
# {'sub': 'user_id', 'email': 'user@example.com', 'exp': 1234567890}

# Access token yenile
new_access = jwt.refresh_access_token(refresh_token)
```

**Token Lifetimes:**
- Access Token: 15 dakika (güvenlik)
- Refresh Token: 7 gün (convenience)

---

### 2. Auth Service (Login Flow)

```python
from auth_service import AuthService

auth = AuthService()

# 1. Register
result = auth.register_user("username", "email@example.com", "password123")

# 2. Login (No 2FA)
result = auth.login("email@example.com", "password123")
# {
#   "success": True,
#   "access_token": "...",
#   "refresh_token": "..."
# }

# 3. Login (2FA Enabled)
result = auth.login("email@example.com", "password123")
# {
#   "success": False,
#   "requires_2fa": True,
#   "user_id": "...",
#   "email": "..."
# }

# 4. Complete 2FA
result = auth.verify_2fa_and_login("email@example.com", "123456")
# {
#   "success": True,
#   "access_token": "...",
#   "refresh_token": "..."
# }
```

---

### 3. FastAPI Endpoints

#### Server Çalıştırma
```bash
python api_routes.py

# Output:
# ✅ Firebase initialized
# ✅ AuthGuard API ready!
# 📝 Docs: http://localhost:8000/docs
```

#### API Endpoints

**Authentication:**
```bash
# Register
POST /auth/register
Body: {"username": "test", "email": "test@example.com", "password": "pass123"}

# Login (No 2FA)
POST /auth/login
Body: {"email": "test@example.com", "password": "pass123"}
Response: {"access_token": "...", "refresh_token": "..."}

# Login (2FA Enabled)
POST /auth/login
Response: {"requires_2fa": true, "user_id": "...", "email": "..."}

# Verify 2FA
POST /auth/verify-2fa
Body: {"email": "test@example.com", "token": "123456"}
Response: {"access_token": "...", "refresh_token": "..."}

# Refresh Token
POST /auth/refresh
Body: {"refresh_token": "..."}
Response: {"access_token": "..."}
```

**2FA Management (Protected):**
```bash
# Enable 2FA
POST /2fa/enable
Headers: {"Authorization": "Bearer <access_token>"}
Body: {"email": "test@example.com"}
Response: {"qr_code": "data:image/png;base64,...", "secret": "..."}

# Disable 2FA
POST /2fa/disable
Headers: {"Authorization": "Bearer <access_token>"}
Body: {"email": "test@example.com"}

# Get 2FA Status
GET /2fa/status?email=test@example.com
Headers: {"Authorization": "Bearer <access_token>"}
```

**Protected Endpoints:**
```bash
# Current User
GET /me
Headers: {"Authorization": "Bearer <access_token>"}
Response: {"user_id": "...", "email": "..."}

# Dashboard
GET /dashboard
Headers: {"Authorization": "Bearer <access_token>"}
```

---

### 4. Frontend React Context

```jsx
import { AuthProvider, useAuth } from './contexts/AuthContext';

// App.js
function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
      </Routes>
    </AuthProvider>
  );
}

// Login Component
function Login() {
  const { login, requires2FA, verify2FA } = useAuth();
  
  const handleLogin = async () => {
    const result = await login(email, password);
    
    if (result.requires2fa) {
      // Show 2FA input
      setShow2FAInput(true);
    } else if (result.success) {
      // Redirect to dashboard
      navigate('/dashboard');
    }
  };
  
  const handle2FA = async () => {
    const result = await verify2FA(code);
    if (result.success) {
      navigate('/dashboard');
    }
  };
}
```

---

## 🔒 Güvenlik Özellikleri

### Hafta 1-3 ✅
- Firebase Admin SDK
- AES-256 encryption
- MD5 deterministic IDs
- RFC 6238 TOTP
- QR code generation

### Hafta 4 ✅ (YENİ)
- **JWT HS256** - HMAC-SHA256 imzalı tokenlar
- **Short-lived Access Tokens** - 15 dakika (güvenlik)
- **Long-lived Refresh Tokens** - 7 gün (UX)
- **Bcrypt Password Hashing** - Salt + hashing
- **Token Verification Middleware** - Protected route'lar
- **Conditional Login Flow** - 2FA-aware state machine
- **CORS Configuration** - React frontend uyumluluğu
- **HTTP Status Codes** - 202 Accepted for 2FA required

---

## 🔄 Login Flow Diyagramı

```
User Login Request
       |
       v
Password Check
       |
       ├─── Invalid ──> 401 Unauthorized
       |
       v
   Valid Password
       |
       v
  2FA Enabled?
       |
       ├─── No ──> Return JWT Tokens (200 OK)
       |
       v
     Yes
       |
       v
Return 2FA_REQUIRED (202 Accepted)
       |
       v
User Enters 6-Digit Code
       |
       v
TOTP Verification
       |
       ├─── Invalid ──> 401 Unauthorized
       |
       v
   Valid Code
       |
       v
Return JWT Tokens (200 OK)
```

---

## 🧪 Test

### Backend Tests
```bash
# JWT Manager
python jwt_manager.py

# Auth Service
python auth_service.py

# FastAPI Server
python api_routes.py
```

### API Test (curl)
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Protected Endpoint
curl http://localhost:8000/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 📊 Token Yapısı

### Access Token Payload
```json
{
  "sub": "55502f40dc8b7c769880b10874abc9d0",  // user_id
  "email": "test@example.com",
  "type": "access",
  "iat": 1701234567,  // Issued at
  "exp": 1701235467   // Expires at (+15 min)
}
```

### Refresh Token Payload
```json
{
  "sub": "55502f40dc8b7c769880b10874abc9d0",
  "email": "test@example.com",
  "type": "refresh",
  "iat": 1701234567,
  "exp": 1701839367   // Expires at (+7 days)
}
```

---

## 🎯 Sprint 4 Tamamlanan Görevler

### Backend ✅
- [x] JWT Manager implementation (HS256)
- [x] Access Token (15 min) generation
- [x] Refresh Token (7 day) generation
- [x] Token verification logic
- [x] Bcrypt password hashing
- [x] Login flow state machine
- [x] Conditional 2FA logic
- [x] Auth Service layer
- [x] FastAPI endpoints
- [x] CORS configuration
- [x] Protected route middleware
- [x] Session storage (Firestore)

### Frontend ✅
- [x] React project structure
- [x] AuthContext (global state)
- [x] useAuth custom hook
- [x] Login/Register functions
- [x] 2FA verification flow
- [x] ProtectedRoute component
- [x] Token storage (localStorage)
- [x] Fetch API integration

---

## 💡 Önemli Notlar (Hafta 4)

### JWT Security
- Secret key minimum 32 karakter olmalı
- Production'da environment variable kullan
- Token'ları HTTPS üzerinden gönder

### Token Storage
- **Development:** localStorage (basit, test için)
- **Production:** HttpOnly cookies (XSS koruması)

### Password Hashing
- bcrypt otomatik salt oluşturur
- Hash verify süresi ~100-200ms (brute-force koruması)

### API Response Codes
- 200 OK - Success
- 202 Accepted - 2FA required
- 401 Unauthorized - Invalid credentials/token
- 400 Bad Request - Validation error

---

## 🚀 Sonraki Adımlar (Hafta 5-6)

- [ ] React UI components (Login, Register, Dashboard)
- [ ] QR Code display component
- [ ] 2FA setup wizard
- [ ] Token refresh logic (auto)
- [ ] Error handling improvements
- [ ] Rate limiting (brute-force)
- [ ] Backup codes system
- [ ] Email verification
- [ ] Password reset flow
- [ ] Production deployment

---

## 📞 API Documentation

FastAPI otomatik olarak interactive docs oluşturur:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**Hafta 4 Tamamlandı! Backend + Frontend infrastructure hazır! 🎉**

**İlerleme:** 67% (4/6 hafta)  
**Tamamlanan:** Firebase, Encryption, 2FA Core, JWT Session  
**Sonraki:** UI Components & Integration
