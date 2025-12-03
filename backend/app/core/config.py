from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Security Analysis (Kişi 3): Veritabanı URL'i ve Secret Key ortam değişkenlerinden okunmalı.
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    
    # Security Analysis (Kişi 3): Token süreleri ayrıştırıldı.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Kısa ömürlü (Güvenlik)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Uzun ömürlü (UX)

    # Security Analysis (Kişi 3): Encryption at Rest için anahtar (Fernet key)
    # Bu anahtar hassas verileri (TOTP secret vb.) veritabanında şifreli saklamak için kullanılır.
    # Üretmek için: cryptography.fernet.Fernet.generate_key()
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY") 

    class Config:
        env_file = ".env"

settings = Settings()