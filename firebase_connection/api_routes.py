from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from auth_service import AuthService
from secure_2fa_operations import Secure2FAOperations
from firebase_config import FirebaseConfig

# FastAPI app
app = FastAPI(
    title="AuthGuard API",
    description="2FA-Enabled Session Management Platform",
    version="0.4.0"
)

# CORS middleware (React frontend için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Services
auth_service = AuthService()
twofa_service = Secure2FAOperations()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Verify2FARequest(BaseModel):
    email: EmailStr
    token: str  # 6-digit code

class Enable2FARequest(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    message: str

class Login2FARequiredResponse(BaseModel):
    requires_2fa: bool
    user_id: str
    email: str
    message: str

# ============================================================================
# DEPENDENCY: AUTH MIDDLEWARE
# ============================================================================

async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Protected route için JWT doğrulama
    
    Usage:
        @app.get("/protected")
        def protected(user=Depends(verify_token_dependency)):
            return {"user": user}
    """
    token = credentials.credentials
    
    user_data = auth_service.verify_access_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/auth/register", response_model=MessageResponse)
async def register(request: RegisterRequest):
    """
    Yeni kullanıcı kaydı
    
    - **username**: Kullanıcı adı
    - **email**: Email adresi
    - **password**: Şifre (min 8 karakter)
    """
    result = auth_service.register_user(
        username=request.username,
        email=request.email,
        password=request.password
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['message']
        )
    
    return MessageResponse(message=result['message'])

@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Login endpoint - Conditional flow
    
    Returns:
    - 200 + JWT tokens (2FA disabled)
    - 202 + requires_2fa (2FA enabled)
    - 401 (invalid credentials)
    """
    result = auth_service.login(
        email=request.email,
        password=request.password
    )
    
    # Case 1: 2FA Required (HTTP 202 Accepted)
    if result.get('requires_2fa'):
        return Login2FARequiredResponse(
            requires_2fa=True,
            user_id=result['user_id'],
            email=result['email'],
            message=result['message']
        )
    
    # Case 2: Invalid Credentials
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result['message']
        )
    
    # Case 3: Success - Return JWT tokens
    return TokenResponse(
        access_token=result['access_token'],
        refresh_token=result['refresh_token'],
        token_type=result['token_type']
    )

@app.post("/auth/verify-2fa", response_model=TokenResponse)
async def verify_2fa(request: Verify2FARequest):
    """
    2FA kod doğrulama ve JWT token alma
    
    - **email**: User email
    - **token**: 6-digit TOTP code
    """
    result = auth_service.verify_2fa_and_login(
        email=request.email,
        token=request.token
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result['message']
        )
    
    return TokenResponse(
        access_token=result['access_token'],
        refresh_token=result['refresh_token'],
        token_type=result['token_type']
    )

@app.post("/auth/refresh", response_model=dict)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh token ile yeni access token al
    """
    result = auth_service.refresh_token(request.refresh_token)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    return result

# ============================================================================
# 2FA ENDPOINTS
# ============================================================================

@app.post("/2fa/enable")
async def enable_2fa(
    request: Enable2FARequest,
    user: dict = Depends(verify_token_dependency)
):
    """
    2FA'yı aktifleştir ve QR kod al (Protected)
    
    Returns:
        - qr_code: Base64 PNG image
        - secret: TOTP secret (manual entry için)
    """
    result = twofa_service.enable_2fa(request.email)
    
    return {
        "qr_code": result['qr_code'],
        "secret": result['secret'],
        "message": "2FA enabled successfully"
    }

@app.post("/2fa/disable")
async def disable_2fa(
    email: EmailStr,
    user: dict = Depends(verify_token_dependency)
):
    """
    2FA'yı devre dışı bırak (Protected)
    """
    result = twofa_service.disable_2fa(email)
    
    return MessageResponse(message="2FA disabled successfully")

@app.get("/2fa/status")
async def get_2fa_status(
    email: EmailStr,
    user: dict = Depends(verify_token_dependency)
):
    """
    2FA durumunu kontrol et (Protected)
    """
    status_data = twofa_service.get_2fa_status(email)
    
    return status_data

# ============================================================================
# PROTECTED ENDPOINTS (Example)
# ============================================================================

@app.get("/me")
async def get_current_user(user: dict = Depends(verify_token_dependency)):
    """
    Mevcut kullanıcı bilgisi (Protected)
    
    Requires: Bearer token in Authorization header
    """
    return {
        "user_id": user['user_id'],
        "email": user['email'],
        "message": "You are authenticated!"
    }

@app.get("/dashboard")
async def dashboard(user: dict = Depends(verify_token_dependency)):
    """
    Dashboard (Protected)
    """
    return {
        "message": f"Welcome to your dashboard, {user['email']}!",
        "user_id": user['user_id']
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """
    API Health check
    """
    return {
        "name": "AuthGuard API",
        "version": "0.4.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """
    Detailed health check
    """
    return {
        "status": "healthy",
        "firebase": "connected",
        "jwt": "enabled",
        "2fa": "enabled"
    }

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    App başlatılırken Firebase'i initialize et
    """
    FirebaseConfig.initialize()
    print("✅ Firebase initialized")
    print("✅ AuthGuard API ready!")
    print("📝 Docs: http://localhost:8000/docs")

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting AuthGuard API Server...")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Development mode
    )
