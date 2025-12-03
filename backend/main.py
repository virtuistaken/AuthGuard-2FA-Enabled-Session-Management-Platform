from fastapi import FastAPI
from app.auth import router as auth_router
from app.db.session import engine, Base

# Veritabanı tablolarını oluştur (Migration yoksa otomatik oluşturur)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AuthGuard API", version="0.1.0")

app.include_router(auth_router.router)

@app.get("/health")
def health_check():
    return {"status": "active", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)