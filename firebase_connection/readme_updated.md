# 🔥 Firebase & Cloud Backend - HAFTA 3 Güncellemesi

AuthGuard projesi için Firebase Firestore + 2FA entegrasyonu

## 🆕 Hafta 3 Yenilikleri

### ✅ Yeni Eklenen Modüller
- **totp_manager.py** - RFC 6238 uyumlu TOTP implementasyonu
- **secure_2fa_operations.py** - Şifreli 2FA operasyonları

### ✅ Yeni Özellikler
- 256-bit TOTP secret üretimi
- QR kod oluşturma (base64 PNG)
- 6-digit kod doğrulama
- Clock drift toleransı (±30 saniye)
- Otomatik şifreleme entegrasyonu

---

## 📦 Kurulum

### 1. Gereksinimleri Yükle
```bash
pip install -r requirements_firebase.txt
```

**Yeni eklenen paketler (Hafta 3):**
- `pyotp==2.9.0` - TOTP algoritması
- `qrcode[pil]==7.4.2` - QR kod oluşturma

---

## 🗂️ Güncel Dosya Yapısı

```
firebase_backend/
├── requirements_firebase.txt    # Güncellenmiş paketler (pyotp, qrcode eklendi)
├── .env.example                 # Environment örneği
│
├── firebase_config.py           # Firebase bağlantısı
├── data_schema.py               # Firestore veri şeması
├── crud_operations.py           # Basit CRUD (Hafta 1)
│
├── encryption.py                # Şifreleme modülü (Hafta 2)
├── md5_docid.py                 # MD5 doc_id sistemi (Hafta 2)
├── secure_operations.py         # Şifreli işlemler (Hafta 2)
│
├── totp_manager.py              # 🆕 TOTP yönetimi (Hafta 3)
└── secure_2fa_operations.py     # 🆕 2FA operasyonları (Hafta 3)
```

---

## 🔐 HAFTA 3: 2FA Core Implementation

### 1. TOTP Manager

```python
from totp_manager import TOTPManager

totp = TOTPManager(issuer_name="AuthGuard")

# Secret üret
secret = totp.generate_secret()
# Output: "JBSWY3DPEHPK3PXP" (32 karakter base32)

# QR kod oluştur
qr_code = totp.generate_qr_code("user@example.com", secret)
# Output: "data:image/png;base64,iVBORw0KG..." (base64 PNG)

# Token doğrula
is_valid = totp.verify_token(secret, "123456")

# Şu anki token'ı al (test için)
current = totp.get_current_token(secret)
print(f"Current token: {current}")
```

### 2. Secure 2FA Operations (Entegre)

```python
from secure_2fa_operations import Secure2FAOperations

ops = Secure2FAOperations()

# 2FA aktifleştir
result = ops.enable_2fa("user@example.com")
# {
#   'user_id': 'md5_hash',
#   'secret': 'JBSWY3DPEHPK3PXP',
#   'qr_code': 'data:image/png;base64,...',
#   'manual_entry_key': 'JBSWY3DPEHPK3PXP'
# }

# QR kodu frontend'e gönder
print(result['qr_code'])  # <img src="..." /> ile göster

# Token doğrula
is_valid = ops.verify_2fa_token("user@example.com", "123456")

# 2FA durumunu kontrol et
status = ops.get_2fa_status("user@example.com")
# {'is_enabled': True, 'last_used': datetime, 'created_at': datetime}

# 2FA'yı devre dışı bırak
ops.disable_2fa("user@example.com")
```

---

## 🔒 Güvenlik Özellikleri

### Hafta 1 ✅
- Firebase Admin SDK authentication
- Service account key güvenliği
- Firestore security rules
- Indexing optimization

### Hafta 2 ✅
- AES-256 encryption (Fernet)
- Field-level encryption
- Encrypted field markers
- MD5 deterministic IDs
- Automatic encrypt/decrypt
- Secure key management

### Hafta 3 ✅ (YENİ)
- **RFC 6238 uyumlu TOTP** - Standart Time-based OTP algoritması
- **256-bit secret keys** - pyotp.random_base32() ile güvenli üretim
- **QR kod üretimi** - Google/Microsoft Authenticator uyumlu
- **Clock drift toleransı** - ±30 saniye time window
- **Otomatik şifreleme** - Secret'lar Firestore'a encrypted kaydedilir
- **Replay attack koruması** - Token yalnızca bir kez geçerli
- **Last used tracking** - Her başarılı doğrulamada timestamp güncellenir

---

## 🧪 Test

### Hafta 3 Testleri
```bash
# TOTP Manager test
python totp_manager.py

# Secure 2FA Operations test
python secure_2fa_operations.py
```

### Örnek Test Çıktısı
```
🔐 2FA Aktifleştirme Başlatıldı: test@example.com
============================================================
   ✅ Secret oluşturuldu: JBSWY3DP...
   ✅ QR kod oluşturuldu
   ✅ Şifreli secret Firestore'a kaydedildi
   📍 Document ID: 55502f40dc8b7c769880b10874abc9d0

✅ 2FA başarıyla aktifleştirildi!
============================================================

🔍 2FA Token Doğrulama: test@example.com
============================================================
   ✅ Secret çözüldü: JBSWY3DP...
   ✅ Token geçerli!
   ⏰ Kalan süre: 25s
============================================================
```

---

## 📊 Firestore Koleksiyonları (Güncellenmiş)

### two_factor_auth
```
Document ID: user_id (MD5 of email)
{
  user_id: string
  secret_key: string (🆕 encrypted TOTP secret)
  backup_codes: array
  created_at: timestamp
  last_used: timestamp (🆕 her doğrulamada güncellenir)
  is_enabled: boolean
  secret_key_encrypted: boolean (🆕 encryption marker)
}
```

---

## 🎯 Sprint 3 Tamamlanan Görevler

- [x] pyotp kütüphanesi entegrasyonu
- [x] 256-bit TOTP secret üretimi
- [x] QR kod oluşturma (base64 PNG)
- [x] otpauth:// URI formatı
- [x] 6-digit kod doğrulama
- [x] Clock drift toleransı (±30s)
- [x] Encryption entegrasyonu
- [x] Firestore'a şifreli kaydetme
- [x] Last used tracking
- [x] 2FA enable/disable API logic
- [x] Unit testler

---

## 📱 2FA Kullanım Akışı

### 1. Kullanıcı 2FA'yı Aktifleştirir
```
POST /api/2fa/enable
Response: {
  "qr_code": "data:image/png;base64,...",
  "manual_entry_key": "JBSWY3DPEHPK3PXP"
}
```

### 2. Kullanıcı QR Kodu Tarar
- Google Authenticator açılır
- "+" butonuna basılır
- QR kod taranır
- 6-digit kod görünür

### 3. Kullanıcı Kodu Doğrular
```
POST /api/2fa/verify
Body: {"token": "123456"}
Response: {"valid": true}
```

### 4. Login Akışı (2FA ile)
```
1. POST /auth/login → username + password
2. If user.is_2fa_enabled:
   → Return {"requires_2fa": true}
3. POST /auth/2fa/verify → 6-digit token
4. If valid → Return JWT access token
```

---

## 💡 Önemli Notlar (Hafta 3)

- **Time Sync:** Sunucu saatinin NTP ile senkron olması kritik
- **Window Toleransı:** `verify_token(window=1)` ile ±30 saniye tolerans
- **Secret Güvenliği:** Secret'lar asla plain text saklanmaz, her zaman encrypted
- **QR Format:** `data:image/png;base64,...` formatı direkt `<img src="">` ile kullanılabilir
- **Token Lifetime:** Her token 30 saniye geçerli, sonra yenisi üretilir

---

## 🚀 Sonraki Adımlar (Hafta 4)

- [ ] FastAPI endpoint'leri (/api/2fa/enable, /api/2fa/verify)
- [ ] JWT token generation
- [ ] Session management
- [ ] Rate limiting (brute-force koruması)
- [ ] Backup codes sistemi
- [ ] Frontend entegrasyonu

---

## 📞 Yardım

- **pyotp Docs:** https://pyauth.github.io/pyotp/
- **RFC 6238:** https://tools.ietf.org/html/rfc6238
- **QR Code Docs:** https://github.com/lincolnloop/python-qrcode

---

**Hafta 3 Tamamlandı! 2FA Core hazır! 🎉**
