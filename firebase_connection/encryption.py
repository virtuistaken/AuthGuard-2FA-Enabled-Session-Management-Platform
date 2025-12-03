from cryptography.fernet import Fernet
import os
import base64

class EncryptionModule:
    """
    Basit şifreleme modülü
    Fernet (AES-128 CBC + HMAC) kullanır
    """
    
    def __init__(self, key: bytes = None):
        """
        Args:
            key: 32-byte encryption key (base64 encoded)
                 None ise environment'tan alır veya yeni oluşturur
        """
        if key is None:
            # Environment'tan al
            key_str = os.getenv('ENCRYPTION_KEY')
            if key_str:
                key = key_str.encode()
            else:
                # Yeni key oluştur
                key = Fernet.generate_key()
                print(f"⚠️  Yeni encryption key oluşturuldu!")
                print(f"🔑 Key: {key.decode()}")
                print("⚠️  Bu key'i .env dosyasına kaydet: ENCRYPTION_KEY={key}")
        
        self.cipher = Fernet(key)
        self.key = key
    
    def encrypt(self, data: str) -> str:
        """
        String'i şifrele
        
        Args:
            data: Şifrelenecek metin
            
        Returns:
            Şifrelenmiş metin (base64 encoded)
        """
        if not data:
            return ""
        
        # String'i byte'a çevir
        data_bytes = data.encode('utf-8')
        
        # Şifrele
        encrypted_bytes = self.cipher.encrypt(data_bytes)
        
        # Base64 string olarak döndür
        encrypted_str = encrypted_bytes.decode('utf-8')
        
        return encrypted_str
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Şifreli string'i çöz
        
        Args:
            encrypted_data: Şifrelenmiş metin
            
        Returns:
            Orijinal metin
        """
        if not encrypted_data:
            return ""
        
        # String'i byte'a çevir
        encrypted_bytes = encrypted_data.encode('utf-8')
        
        # Şifreyi çöz
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        
        # String'e çevir
        decrypted_str = decrypted_bytes.decode('utf-8')
        
        return decrypted_str
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Dictionary'deki belirli alanları şifrele
        
        Args:
            data: Şifrelenecek dictionary
            fields_to_encrypt: Şifrelenecek alan isimleri
            
        Returns:
            Şifrelenmiş dictionary
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
                # Şifrelendiğini işaretle
                encrypted_data[f"{field}_encrypted"] = True
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Dictionary'deki şifreli alanları çöz
        
        Args:
            data: Şifreli dictionary
            fields_to_decrypt: Çözülecek alan isimleri
            
        Returns:
            Çözülmüş dictionary
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data.get(f"{field}_encrypted"):
                decrypted_data[field] = self.decrypt(decrypted_data[field])
                # Şifreleme flag'ini kaldır
                decrypted_data.pop(f"{field}_encrypted", None)
        
        return decrypted_data


# Test
if __name__ == "__main__":
    print("🔐 Encryption Module Test\n")
    
    # Encryption instance
    enc = EncryptionModule()
    
    # Test 1: Basit şifreleme
    print("1️⃣ String Encryption")
    original = "MySecretPassword123!"
    encrypted = enc.encrypt(original)
    decrypted = enc.decrypt(encrypted)
    
    print(f"Original:  {original}")
    print(f"Encrypted: {encrypted[:50]}...")
    print(f"Decrypted: {decrypted}")
    print(f"✅ Match: {original == decrypted}\n")
    
    # Test 2: Dictionary şifreleme
    print("2️⃣ Dictionary Encryption")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SuperSecret123",
        "totp_secret": "JBSWY3DPEHPK3PXP"
    }
    
    print("Original data:")
    for key, value in user_data.items():
        print(f"   {key}: {value}")
    
    # Şifrele
    encrypted_data = enc.encrypt_dict(
        user_data,
        fields_to_encrypt=['password', 'totp_secret']
    )
    
    print("\nEncrypted data:")
    for key, value in encrypted_data.items():
        if 'password' in key or 'secret' in key:
            print(f"   {key}: {str(value)[:50]}...")
        else:
            print(f"   {key}: {value}")
    
    # Çöz
    decrypted_data = enc.decrypt_dict(
        encrypted_data,
        fields_to_decrypt=['password', 'totp_secret']
    )
    
    print("\nDecrypted data:")
    for key, value in decrypted_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Password match: {user_data['password'] == decrypted_data['password']}")
    print(f"✅ Secret match: {user_data['totp_secret'] == decrypted_data['totp_secret']}")
