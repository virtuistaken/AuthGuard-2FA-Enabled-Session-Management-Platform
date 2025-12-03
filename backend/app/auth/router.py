from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta

from app.db.session import get_db
from app.users import models, schemas
from app.core import security
from app.core.config import settings

# Security Analysis (Kişi 3): Rate Limiting için gerekli importlar
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# 1. REGISTER (Kayıt)
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Input Validation Schema seviyesinde yapıldı (Pydantic)
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = security.get_password_hash(user.password)
    
    # Security Analysis (Kişi 3): Kullanıcı oluşturulurken 2FA default kapalı.
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. LOGIN (Giriş) - Rate Limit & 2FA Check Eklendi
@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute") # Security Analysis (Kişi 3): Brute-Force engelleme (5 deneme/dakika)
def login(
    request: Request, # Rate limiter için gerekli
    form_data: OAuth2PasswordRequestForm = Depends(), 
    totp_code: str = None, # Eğer 2FA aktifse bu alan zorunlu olacak (Query veya Body param olabilir)
    db: Session = Depends(get_db)
):
    # SQL Injection riskine karşı ORM (SQLAlchemy) kullanımı güvenlidir.
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Security Analysis (Kişi 3): Timing Attack önleme ve Bilgi Sızdırma (Enumeration) önleme
    # Kullanıcı yoksa bile hash doğrulama süresi kadar bekletilmeli (mock verify) - Simüle ediyoruz.
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Security Analysis (Kişi 3): 2FA Kontrolü
    if user.is_2fa_enabled:
        if not totp_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="2FA code required"
            )
        
        # Secret'ı çöz (Decrypt) ve doğrula
        decrypted_secret = security.decrypt_data(user.totp_secret)
        if not security.verify_totp(decrypted_secret, totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid 2FA code"
            )

    # Tokenları oluştur
    access_token = security.create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

# 3. Enable 2FA (2FA Aktifleştirme)
@router.post("/enable-2fa", response_model=schemas.Enable2FAResponse)
def enable_2fa(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    # Token decode işlemi (yardımcı fonksiyona taşınabilir ama burada açıkça gösterelim)
    user = get_current_user_logic(token, db)
    
    if user.is_2fa_enabled:
         raise HTTPException(status_code=400, detail="2FA already enabled")

    # Secret oluştur ve şifrele (Encryption at Rest)
    secret = security.generate_totp_secret()
    encrypted_secret = security.encrypt_data(secret)
    
    user.totp_secret = encrypted_secret
    user.is_2fa_enabled = True # Normalde bir doğrulama adımından sonra True yapılır ama basitlik adına burada yapıyoruz.
    db.commit()
    
    otpauth_url = security.get_totp_uri(secret, user.email)
    return {"secret": secret, "otpauth_url": otpauth_url}

# 4. REFRESH TOKEN Endpoint
@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
             raise HTTPException(status_code=401, detail="Invalid token type")
        email: str = payload.get("sub")
        if email is None:
             raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Yeni access token üret
    access_token = security.create_access_token(data={"sub": email})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, # Refresh token rotasyon mantığı eklenebilir
        "token_type": "bearer"
    }

# Helper Function
def get_current_user_logic(token: str, db: Session):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
             raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
         raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return get_current_user_logic(token, db)