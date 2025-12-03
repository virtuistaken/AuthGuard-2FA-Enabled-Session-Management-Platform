from datetime import datetime
from typing import Dict, Any

class FirestoreSchema:
    """
    Firestore veri şeması tanımları
    3 ana koleksiyon: users, sessions, two_factor_auth
    """
    
    @staticmethod
    def user_document(username: str, email: str, hashed_password: str) -> Dict[str, Any]:
        """
        Users koleksiyonu için document şeması
        
        Collection: users
        Document ID: {user_id} veya MD5 hash
        """
        return {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "is_2fa_enabled": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "status": "active"  # active, suspended, deleted
        }
    
    @staticmethod
    def session_document(user_id: str, access_token: str, refresh_token: str) -> Dict[str, Any]:
        """
        Sessions koleksiyonu için document şeması
        
        Collection: sessions
        Document ID: {session_id} veya MD5 hash
        """
        return {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow(),
            "expires_at": None,  # Token expiry time
            "ip_address": None,
            "user_agent": None,
            "is_active": True
        }
    
    @staticmethod
    def two_factor_auth_document(user_id: str, secret_key: str) -> Dict[str, Any]:
        """
        Two-factor authentication koleksiyonu için document şeması
        
        Collection: two_factor_auth
        Document ID: {user_id}
        """
        return {
            "user_id": user_id,
            "secret_key": secret_key,  # TOTP secret (encrypted)
            "backup_codes": [],  # List of backup codes
            "created_at": datetime.utcnow(),
            "last_used": None,
            "is_enabled": False
        }
    
    @staticmethod
    def get_collections():
        """Tüm koleksiyon isimlerini döndür"""
        return {
            "users": "users",
            "sessions": "sessions",
            "two_factor_auth": "two_factor_auth"
        }


# Test - Şema örnekleri
if __name__ == "__main__":
    print("📋 Firestore Veri Şeması\n")
    
    # User document örneği
    user_doc = FirestoreSchema.user_document(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$hash..."
    )
    print("1. USER DOCUMENT:")
    for key, value in user_doc.items():
        print(f"   {key}: {value}")
    
    print("\n2. SESSION DOCUMENT:")
    session_doc = FirestoreSchema.session_document(
        user_id="user123",
        access_token="jwt.access.token",
        refresh_token="jwt.refresh.token"
    )
    for key, value in session_doc.items():
        print(f"   {key}: {value}")
    
    print("\n3. TWO_FACTOR_AUTH DOCUMENT:")
    tfa_doc = FirestoreSchema.two_factor_auth_document(
        user_id="user123",
        secret_key="JBSWY3DPEHPK3PXP"
    )
    for key, value in tfa_doc.items():
        print(f"   {key}: {value}")
    
    print("\n📁 Koleksiyonlar:")
    collections = FirestoreSchema.get_collections()
    for key, value in collections.items():
        print(f"   - {value}")
