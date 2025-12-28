from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.users import models, schemas
from app.core import security
from app.core.config import settings

# Rate Limiter Tanımlaması
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- 1. REGISTER (Kayıt Ol) ---
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- 2. LOGIN (Giriş Yap) ---
@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute") # Dakikada maksimum 5 deneme (Brute-Force Koruması)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    totp_code: str = None, # 2FA Kodu (Opsiyonel)
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Kullanıcı yoksa veya şifre yanlışsa
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2FA Kontrolü (Eğer kullanıcıda aktifse)
    if user.is_2fa_enabled:
        if not totp_code:
            raise HTTPException(status_code=403, detail="2FA code required")
        
        # Şifreli secret'ı çöz ve doğrula
        decrypted_secret = security.decrypt_data(user.totp_secret)
        if not security.verify_totp(decrypted_secret, totp_code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")

    # Tokenları Üret
    access_token = security.create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "refresh_token": "not_implemented_yet", "token_type": "bearer"}

# --- 3. ENABLE 2FA (2FA Aktifleştir) ---
@router.post("/enable-2fa", response_model=schemas.Enable2FAResponse)
def enable_2fa(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user_logic(token, db)
    
    if user.is_2fa_enabled:
         raise HTTPException(status_code=400, detail="2FA already enabled")

    # Secret oluştur ve VERİTABANINA ŞİFRELEYEREK kaydet (Encryption at Rest)
    secret = security.generate_totp_secret()
    encrypted_secret = security.encrypt_data(secret)
    
    user.totp_secret = encrypted_secret
    user.is_2fa_enabled = True
    db.commit()
    
    otpauth_url = security.get_totp_uri(secret, user.email)
    return {"secret": secret, "otpauth_url": otpauth_url}

# --- YARDIMCI FONKSİYON ---
def get_current_user_logic(token: str, db: Session):
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise HTTPException(status_code=401, detail="User not found")
    return user