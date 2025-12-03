from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base

class User(Base):
    __tablename__ = "users"  # <--- BU SATIR EKSİK OLDUĞU İÇİN HATA ALIYORDUNUZ

    id = Column(Integer, primary_key=True, index=True)
    
    # Security Analysis (Kişi 3): Email indexleniyor, sorgu performansı ve unique constraint önemli.
    email = Column(String, unique=True, index=True, nullable=False)
    
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Security Analysis (Kişi 3): 2FA Alanları eklendi.
    # totp_secret veritabanında ASLA düz metin (plain text) saklanmayacak.
    # security.encrypt_data ile şifrelenip kaydedilecek.
    totp_secret = Column(String, nullable=True) 
    is_2fa_enabled = Column(Boolean, default=False)