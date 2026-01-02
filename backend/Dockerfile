# Base Image: Hafif ve güvenli (Sprint 5 - Task 1)
FROM python:3.10-slim

# Çevresel Değişkenler
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (psycopg2 için gerekebilir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Güvenlik: Root olmayan kullanıcı oluştur (Sprint 5 - Task 1)
RUN useradd -m appuser
USER appuser

# Port
EXPOSE 8000

# Başlatma komutu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
