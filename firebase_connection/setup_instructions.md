# 🚀 AuthGuard Setup Guide - Hafta 4

## Kurulum Adımları

### 1. Python Dependencies
```bash
cd backend/
pip install -r requirements_firebase.txt
```

### 2. Environment Variables
`.env` dosyası oluştur:
```bash
# Firebase
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json

# Encryption (Week 2)
ENCRYPTION_KEY=your-fernet-key-here

# JWT (Week 4)
JWT_SECRET_KEY=your-secret-key-minimum-32-characters
```

Key oluşturma:
```bash
# Encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Firebase Setup
1. https://console.firebase.google.com
2. Create new project
3. Firestore Database → Enable
4. Project Settings → Service Accounts
5. Generate new private key
6. Save as `serviceAccountKey.json`

### 4. Test Backend
```bash
# Test each module
python firebase_config.py
python encryption.py
python totp_manager.py
python jwt_manager.py
python auth_service.py
```

### 5. Run API Server
```bash
python api_routes.py
```

Server info:
- URL: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. Test API
```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 7. Frontend Setup (Opsiyonel)
```bash
cd frontend/
npm install
npm start
```

React app: http://localhost:3000

---

## Hızlı Test Senaryosu

```bash
# 1. Register user
curl -X POST localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@test.com","password":"Demo123!"}'

# 2. Login (will return JWT)
curl -X POST localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo123!"}'

# Response: {"access_token":"...","refresh_token":"..."}

# 3. Access protected endpoint
curl http://localhost:8000/me \
  -H "Authorization: Bearer <paste_access_token_here>"

# 4. Enable 2FA
curl -X POST localhost:8000/2fa/enable \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com"}'

# Response: {"qr_code":"data:image/png;base64,...","secret":"..."}

# 5. Login again (now requires 2FA)
curl -X POST localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo123!"}'

# Response: {"requires_2fa":true,"user_id":"...","email":"..."}

# 6. Get current TOTP code (for testing)
python -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET_HERE').now())"

# 7. Verify 2FA
curl -X POST localhost:8000/auth/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","token":"123456"}'
```

---

## Troubleshooting

### Firebase Connection Error
```
Error: Could not find serviceAccountKey.json
```
**Çözüm:** Firebase console'dan key indir ve proje root'una koy

### JWT Error
```
Error: JWT_SECRET_KEY not found
```
**Çözüm:** `.env` dosyasına `JWT_SECRET_KEY` ekle

### Import Error
```
ModuleNotFoundError: No module named 'jose'
```
**Çözüm:** `pip install python-jose[cryptography]`

### CORS Error (Frontend)
```
Access to fetch blocked by CORS policy
```
**Çözüm:** `api_routes.py`'de `allow_origins` listesini kontrol et

---

## Dosya Kontrol Listesi

Backend:
- [x] firebase_config.py
- [x] data_schema.py
- [x] crud_operations.py
- [x] encryption.py
- [x] md5_docid.py
- [x] secure_operations.py
- [x] totp_manager.py
- [x] secure_2fa_operations.py
- [x] jwt_manager.py (Week 4)
- [x] auth_service.py (Week 4)
- [x] api_routes.py (Week 4)
- [x] requirements_firebase.txt
- [x] .env
- [x] serviceAccountKey.json

Frontend:
- [x] AuthContext.jsx (Week 4)
- [x] ProtectedRoute.jsx (Week 4)

---

## Port Usage
- Backend API: 8000
- React Frontend: 3000
- Firebase: Cloud

---

## Quick Commands

```bash
# Backend
cd backend/
python api_routes.py

# Frontend (ayrı terminal)
cd frontend/
npm start

# Test
curl http://localhost:8000/health
```

---

✅ Setup tamamlandı! API çalışıyor! 🎉
