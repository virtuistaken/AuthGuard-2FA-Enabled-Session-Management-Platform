from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Validator (Regex) kısmını kaldırdık, hata riskini sıfırladık.
class UserCreate(BaseModel):
    email: EmailStr
    # Sadece en az 8 karakter olma şartı koyuyoruz
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_2fa_enabled: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Enable2FAResponse(BaseModel):
    secret: str
    otpauth_url: str