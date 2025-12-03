from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.config import settings
from cryptography.fernet import Fernet
import pyotp

# Security Analysis (Kişi 3): Argon2 kullanımı modern güvenlik standartları için daha iyidir
# ancak geçiş maliyeti olmaması için Bcrypt'i sıkılaştırılmış ayarlarla kullanıyoruz.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption Suite (Veritabanındaki hassas verileri şifrelemek için)
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

# --- Password Hashing ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- JWT Handling ---
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    # Security Analysis (Kişi 3): Refresh token mekanizması eklendi.
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# --- Encryption at Rest (TOTP Secret) ---
def encrypt_data(data: str) -> str:
    # Hassas veriyi şifreler
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    # Şifreli veriyi çözer
    return cipher_suite.decrypt(token.encode()).decode()

# --- 2FA / TOTP Logic ---
def generate_totp_secret():
    # Yeni bir rastgele 2FA secret oluşturur
    return pyotp.random_base32()

def verify_totp(secret: str, code: str):
    # Kullanıcının girdiği kodun doğruluğunu kontrol eder
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def get_totp_uri(secret: str, email: str):
    # QR kod üretimi için gerekli URI formatı
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="AuthGuard")