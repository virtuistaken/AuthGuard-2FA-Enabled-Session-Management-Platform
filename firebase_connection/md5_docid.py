import hashlib
from datetime import datetime
from typing import Optional

class MD5DocIDGenerator:
    """
    MD5 hash kullanarak deterministik document ID üretir
    """
    
    @staticmethod
    def generate_user_id(email: str) -> str:
        """
        Email'den user_id oluştur
        
        Args:
            email: Kullanıcı email adresi
            
        Returns:
            32 karakterlik MD5 hash
        """
        # Email'i küçük harfe çevir (case-insensitive)
        email_lower = email.lower().strip()
        
        # MD5 hash oluştur
        hash_obj = hashlib.md5(email_lower.encode('utf-8'))
        doc_id = hash_obj.hexdigest()
        
        return doc_id
    
    @staticmethod
    def generate_session_id(user_id: str, timestamp: Optional[str] = None) -> str:
        """
        User ID ve timestamp'ten session_id oluştur
        
        Args:
            user_id: Kullanıcı ID
            timestamp: ISO format timestamp (None ise şimdiki zaman)
            
        Returns:
            32 karakterlik MD5 hash
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        
        # user_id + timestamp birleştir
        combined = f"{user_id}:{timestamp}"
        
        # MD5 hash oluştur
        hash_obj = hashlib.md5(combined.encode('utf-8'))
        doc_id = hash_obj.hexdigest()
        
        return doc_id
    
    @staticmethod
    def generate_2fa_id(user_id: str) -> str:
        """
        2FA için doc_id oluştur (user_id ile aynı)
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            User ID (2FA doc_id = user_id)
        """
        # 2FA için user_id'yi direkt kullan (1-to-1 ilişki)
        return user_id
    
    @staticmethod
    def generate_custom_id(prefix: str, *args) -> str:
        """
        Özel doc_id oluştur
        
        Args:
            prefix: ID prefix (örn: "token", "backup")
            *args: Hash'e dahil edilecek değerler
            
        Returns:
            32 karakterlik MD5 hash
        """
        # Tüm argümanları birleştir
        combined = prefix + ":" + ":".join(str(arg) for arg in args)
        
        # MD5 hash oluştur
        hash_obj = hashlib.md5(combined.encode('utf-8'))
        doc_id = hash_obj.hexdigest()
        
        return doc_id
    
    @staticmethod
    def verify_id(input_data: str, expected_id: str) -> bool:
        """
        ID'nin doğru olup olmadığını kontrol et
        
        Args:
            input_data: Orijinal veri
            expected_id: Beklenen MD5 hash
            
        Returns:
            True eğer hash eşleşirse
        """
        generated_id = hashlib.md5(input_data.encode('utf-8')).hexdigest()
        return generated_id == expected_id


# Test
if __name__ == "__main__":
    print("🔢 MD5 Document ID Generator Test\n")
    
    # Test 1: User ID
    print("1️⃣ User ID Generation")
    email = "test@example.com"
    user_id = MD5DocIDGenerator.generate_user_id(email)
    
    print(f"Email: {email}")
    print(f"User ID: {user_id}")
    print(f"Length: {len(user_id)} characters\n")
    
    # Aynı email -> aynı ID (deterministik)
    user_id2 = MD5DocIDGenerator.generate_user_id(email)
    print(f"✅ Deterministic: {user_id == user_id2}\n")
    
    # Test 2: Session ID
    print("2️⃣ Session ID Generation")
    timestamp = "2024-12-03T10:00:00Z"
    session_id = MD5DocIDGenerator.generate_session_id(user_id, timestamp)
    
    print(f"User ID: {user_id}")
    print(f"Timestamp: {timestamp}")
    print(f"Session ID: {session_id}\n")
    
    # Farklı timestamp -> farklı session ID
    session_id2 = MD5DocIDGenerator.generate_session_id(user_id, "2024-12-03T11:00:00Z")
    print(f"Different timestamp -> Different ID: {session_id != session_id2}\n")
    
    # Test 3: 2FA ID
    print("3️⃣ 2FA ID Generation")
    tfa_id = MD5DocIDGenerator.generate_2fa_id(user_id)
    print(f"User ID: {user_id}")
    print(f"2FA ID: {tfa_id}")
    print(f"✅ Same as User ID: {tfa_id == user_id}\n")
    
    # Test 4: Custom ID
    print("4️⃣ Custom ID Generation")
    token_id = MD5DocIDGenerator.generate_custom_id(
        "refresh_token",
        user_id,
        "device_123",
        datetime.utcnow().isoformat()
    )
    print(f"Token ID: {token_id}\n")
    
    # Test 5: ID Verification
    print("5️⃣ ID Verification")
    is_valid = MD5DocIDGenerator.verify_id(email.lower(), user_id)
    print(f"✅ Valid ID: {is_valid}")
    
    # Özet
    print("\n" + "="*50)
    print("📊 ID Examples:")
    print("="*50)
    print(f"User:    {user_id}")
    print(f"Session: {session_id}")
    print(f"2FA:     {tfa_id}")
    print(f"Token:   {token_id}")
