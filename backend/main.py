from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth import router as auth_router
from app.auth.router import limiter
from app.db.session import engine, Base

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# API Dokümantasyon Metadata (Sprint 4 - Task 4)
tags_metadata = [
    {
        "name": "Auth",
        "description": "Kullanıcı girişi, kayıt ve token işlemleri.",
    },
    {
        "name": "Security",
        "description": "2FA ve Güvenlik ayarları.",
    },
]

app = FastAPI(
    title="AuthGuard API",
    description="Güvenli Kodlama ve 2FA Entegrasyonu Projesi API Dokümantasyonu. Rate Limiting, JWT ve Güvenlik Başlıkları içerir.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- GÜVENLİK KATMANI (Security Analysis - Week 3) ---

# 1. Rate Limiter (Saldırı Önleme)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Security Headers (HTTP Başlık Güvenliği)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Server bilgisini gizle (Security audit bulgusu olabilir)
        del response.headers["server"]
        return response

app.add_middleware(SecurityHeadersMiddleware)

# 3. CORS (Frontend Bağlantısı)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth_router.router, tags=["Auth"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "active", "version": "1.0.0", "security_level": "maximum"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
