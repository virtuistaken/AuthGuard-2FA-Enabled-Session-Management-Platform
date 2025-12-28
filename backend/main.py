from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth import router as auth_router
from app.auth.router import limiter
from app.db.session import engine, Base

# Veritabanı tablolarını otomatik oluştur (Migration yoksa)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AuthGuard API", version="1.0.0")

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
        return response

app.add_middleware(SecurityHeadersMiddleware)

# 3. CORS (Frontend Bağlantısı)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # React uygulamasına izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth_router.router)

@app.get("/health")
def health_check():
    return {"status": "active", "version": "1.0.0", "security": "high"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)