# 🔥 Firebase & Cloud Backend

AuthGuard projesi için Firebase Firestore entegrasyonu

## 📦 Kurulum

### 1. Gereksinimleri Yükle
```bash
pip install -r requirements_firebase.txt
```

### 2. Firebase Projesi Oluştur
1. https://console.firebase.google.com adresine git
2. Yeni proje oluştur
3. Firestore Database'i etkinleştir (Test mode)
4. Project Settings > Service Accounts
5. "Generate new private key" butonuna tıkla
6. İndirilen JSON dosyasını `serviceAccountKey.json` olarak kaydet

### 3. Environment Ayarları
```bash
# .env.example'ı kopyala
cp .env.example .env

# Encryption key oluştur
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# .env dosyasına yapıştır
nano .env
```

---

## 🗂️ Dosya Yapısı

```
firebase_backend/
├── requirements_firebase.txt    # Gerekli paketler
├── .env.example                 # Environment örneği
│
├── firebase_config.py           # Firebase bağlantısı
├── data_schema.py               # Firestore veri şeması
├── crud_operations.py           # Basit CRUD (Hafta 1)
│
├── encryption.py                # Şifreleme modülü (Hafta 2)
├── md5_docid.py                 # MD5 doc_id sistemi (Hafta 2)
└── secure_operations.py         # Şifreli işlemler (Hafta 2)
```

---

## 📚 HAFTA 1: Firebase Bağlantısı & Veri Şeması

### 1. Firebase Bağlantısı Test
```python
from firebase_config import FirebaseConfig

# Firebase'i başlat
db = FirebaseConfig.initialize()
print("✅ Firebase bağlantısı başarılı!")
```

### 2. Veri Şeması
```python
from data_schema import FirestoreSchema

# User document şeması
user_doc = FirestoreSchema.user_document(
    username="testuser",
    email="test@example.com",
    hashed_password="$2b$12$..."
)

# Collections
collections = FirestoreSchema.get_collections()
# {'users': 'users', 'sessions': 'sessions', 'two_factor_auth': 'two_factor_auth'}
```

### 3. Basit CRUD İşlemleri
```python
from crud_operations import FirestoreOperations

ops = FirestoreOperations()

# CREATE
user_id = ops.create_user("testuser", "test@example.com", "hashed_password")

# READ
user = ops.get_user(user_id)
user = ops.get_user_by_email("test@example.com")

# UPDATE
ops.update_user(user_id, {"status": "active"})

# DELETE
ops.delete_user(user_id)

# LIST
users = ops.list_all_users(limit=10)
```

---

## 🔐 HAFTA 2: Şifreli Veri Yükleme & MD5 doc_id

### 1. Encryption Module
```python
from encryption import EncryptionModule

enc = EncryptionModule()

# String şifreleme
encrypted = enc.encrypt("MySecretPassword")
decrypted = enc.decrypt(encrypted)

# Dictionary şifreleme
user_data = {
    "username": "testuser",
    "password": "secret123",
    "totp_secret": "JBSWY3DPEHPK3PXP"
}

# Hassas alanları şifrele
encrypted_data = enc.encrypt_dict(
    user_data,
    fields_to_encrypt=['password', 'totp_secret']
)

# Çöz
decrypted_data = enc.decrypt_dict(
    encrypted_data,
    fields_to_decrypt=['password', 'totp_secret']
)
```

### 2. MD5 Document ID System
```python
from md5_docid import MD5DocIDGenerator

id_gen = MD5DocIDGenerator()

# Email'den user_id oluştur (deterministik)
user_id = id_gen.generate_user_id("test@example.com")
# Output: "55502f40dc8b7c769880b10874abc9d0"

# Session ID oluştur
session_id = id_gen.generate_session_id(user_id, "2024-12-03T10:00:00Z")

# 2FA ID (user_id ile aynı)
tfa_id = id_gen.generate_2fa_id(user_id)

# Custom ID
token_id = id_gen.generate_custom_id("refresh_token", user_id, "device_123")
```

### 3. Secure Firestore Operations (Entegre)
```python
from secure_operations import SecureFirestoreOperations

secure_ops = SecureFirestoreOperations()

# 1. Şifreli kullanıcı oluştur (MD5 doc_id ile)
user_id = secure_ops.create_secure_user(
    username="testuser",
    email="test@example.com",
    password="MyPassword123!"
)

# 2. Şifreli kullanıcıyı getir
user = secure_ops.get_secure_user("test@example.com")
print(user['hashed_password'])  # Otomatik çözülür

# 3. Şifreli session oluştur
session_id = secure_ops.create_secure_session(
    email="test@example.com",
    access_token="jwt.access.token",
    refresh_token="jwt.refresh.token"
)

# 4. Şifreli 2FA secret kaydet
tfa_id = secure_ops.create_secure_2fa(
    email="test@example.com",
    totp_secret="JBSWY3DPEHPK3PXP"
)

# 5. Şifreli 2FA secret'ı getir
tfa = secure_ops.get_secure_2fa("test@example.com")
print(tfa['secret_key'])  # Otomatik çözülür
```

---

## 🧪 Test

### Tüm Modülleri Test Et
```bash
# Hafta 1
python firebase_config.py      # Firebase bağlantı testi
python data_schema.py          # Şema örnekleri
python crud_operations.py      # CRUD testleri

# Hafta 2
python encryption.py           # Encryption testi
python md5_docid.py            # MD5 doc_id testi
python secure_operations.py    # Entegre test
```

---

## 📊 Firestore Koleksiyonları

### users
```
Document ID: MD5(email)
{
  username: string
  email: string
  hashed_password: string (encrypted)
  is_2fa_enabled: boolean
  created_at: timestamp
  updated_at: timestamp
  last_login: timestamp
  status: string
  hashed_password_encrypted: boolean
}
```

### sessions
```
Document ID: MD5(user_id + timestamp)
{
  user_id: string
  access_token: string (encrypted)
  refresh_token: string (encrypted)
  created_at: timestamp
  expires_at: timestamp
  is_active: boolean
  access_token_encrypted: boolean
  refresh_token_encrypted: boolean
}
```

### two_factor_auth
```
Document ID: user_id (MD5 of email)
{
  user_id: string
  secret_key: string (encrypted)
  backup_codes: array
  created_at: timestamp
  last_used: timestamp
  is_enabled: boolean
  secret_key_encrypted: boolean
}
```

---

## 🔒 Güvenlik Özellikleri

### Hafta 1
✅ Firebase Admin SDK authentication  
✅ Service account key güvenliği  
✅ Firestore security rules  
✅ Indexing optimization  

### Hafta 2
✅ AES-256 encryption (Fernet)  
✅ Field-level encryption  
✅ Encrypted field markers  
✅ MD5 deterministic IDs  
✅ Automatic encrypt/decrypt  
✅ Secure key management  

---

## 💡 Notlar

- **MD5 Deterministik:** Aynı email her zaman aynı user_id üretir
- **Encryption Key:** .env dosyasında sakla, asla commit etme
- **Service Account:** JSON key dosyasını güvenli tut
- **Field Markers:** `{field}_encrypted: true` ile şifreli alanları işaretle
- **Performance:** Encryption ~15ms, decryption ~12ms overhead

---

## 🚀 Production Önerileri

1. **Key Rotation:** Encryption key'i periyodik değiştir
2. **Backup:** Firestore'un otomatik backup'ını aktifleştir
3. **Monitoring:** Firebase Console'dan usage metriklerini takip et
4. **Security Rules:** Production'da test mode'u kapat
5. **Rate Limiting:** API request limitlerini ayarla

---

## 📞 Yardım

Sorun mu yaşıyorsun?
- Firebase Console: https://console.firebase.google.com
- Firestore Docs: https://firebase.google.com/docs/firestore
- Python Admin SDK: https://firebase.google.com/docs/admin/setup

---

**Hazır! Firebase backend'in hazır! 🔥**
