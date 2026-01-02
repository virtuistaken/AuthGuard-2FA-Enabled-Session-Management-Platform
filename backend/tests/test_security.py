import pytest
from app.core.security import (
    verify_password, 
    get_password_hash, 
    encrypt_data, 
    decrypt_data, 
    generate_totp_secret
)

# 1. Password Hashing Testleri
def test_password_hashing():
    password = "securePassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

# 2. Encryption at Rest Testleri (Fernet)
def test_encryption_decryption():
    secret_data = "SuperSecretKey"
    encrypted = encrypt_data(secret_data)
    
    assert encrypted != secret_data
    decrypted = decrypt_data(encrypted)
    assert decrypted == secret_data

# 3. TOTP Generation Testi
def test_totp_generation():
    secret = generate_totp_secret()
    assert len(secret) > 0
    assert isinstance(secret, str)
