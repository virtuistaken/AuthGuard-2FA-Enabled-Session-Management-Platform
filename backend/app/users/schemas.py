from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr
    # Security Analysis (Kişi 3): Parola karmaşıklığı zorunlu kılındı (Regex).
    # En az 8 karakter, 1 büyük harf, 1 küçük harf, 1 rakam.
    password: str = Field(..., min_length=8, description="Password must be strong")

    @validator('password')
    def validate_password_strength(cls, v):
        if not re.match(r'^(?=.[a-z])(?=.[A-Z])(?=.\d)[A-Za-z\d@$!%?&]{8,}$', v):
            raise ValueError('Password must contain at least one uppercase, one lowercase and one number')
        return v

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_2fa_enabled: bool # Kullanıcıya 2FA durumunu dönüyoruz

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str # Security Analysis (Kişi 3): Refresh token eklendi
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Enable2FAResponse(BaseModel):
    secret: str
    otpauth_url: str # QR kod oluşturmak için kullanılacak link