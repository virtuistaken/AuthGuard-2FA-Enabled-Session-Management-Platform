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
from fastapi import Form
import pyotp
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

# --- 2. LOGIN (DÜZELTİLMİŞ & GÜVENLİ VERSİYON) ---
@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    totp_code: str = Form(None), # <--- DÜZELTME 1: Form verisi olarak alıyoruz
    db: Session = Depends(get_db)
):
    # 1. Kullanıcı Doğrulama
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 2FA Kontrolü (GERÇEK DOĞRULAMA)
    if user.is_2fa_enabled:
        if not totp_code:
            raise HTTPException(status_code=403, detail="2FA code required") # Kod gelmediyse reddet

        try:
            # DÜZELTME 2: Önce veritabanındaki şifreli secret'ı ÇÖZÜYORUZ
            decrypted_secret = security.decrypt_data(user.totp_secret)
            
            # Çözülmüş (saf) secret ile doğrulayıcı oluşturuyoruz
            totp = pyotp.TOTP(decrypted_secret)

            # Debug için (İsteğe bağlı - çalışınca silersin)
            print(f"Sunucu Beklenen Kod: {totp.now()} | Gelen Kod: {totp_code}")

            # valid_window=1: Saat farkı toleransı (+-30 saniye)
            if not totp.verify(totp_code, valid_window=1):
                raise HTTPException(status_code=401, detail="Invalid 2FA code")
                
        except Exception as e:
            print(f"2FA Hatası: {str(e)}")
            # Şifre çözme hatası veya başka bir sorun olursa güvenli şekilde reddet
            raise HTTPException(status_code=401, detail="Invalid 2FA code")

    # 3. Token Üretme
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
