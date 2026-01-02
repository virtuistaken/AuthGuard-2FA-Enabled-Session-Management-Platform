from firebase_config import FirebaseConfig
from md5_docid import MD5DocIDGenerator
from encryption import EncryptionModule
from secure_2fa_operations import Secure2FAOperations
from jwt_manager import JWTManager
import bcrypt
from typing import Dict, Optional
from datetime import datetime

class AuthService:
    """
    Authentication Service - Login Flow Logic
    HAFTA 4 - Sprint 4 Implementation
    
    Login States:
    1. PASSWORD_SUCCESS + NO_2FA → Return JWT immediately
    2. PASSWORD_SUCCESS + 2FA_ENABLED → Return 2FA_REQUIRED
    3. 2FA_SUCCESS → Return JWT
    4. FAILURE → Return error
    """
    
    def __init__(self):
        self.db = FirebaseConfig.get_db()
        self.id_gen = MD5DocIDGenerator()
        self.encryption = EncryptionModule()
        self.twofa = Secure2FAOperations()
        self.jwt = JWTManager()
        self.collections = {
            "users": "users",
            "sessions": "sessions"
        }
    
    def register_user(self, username: str, email: str, password: str) -> Dict:
        """
        Yeni kullanıcı kaydı (password hashing ile)
        
        Args:
            username: Kullanıcı adı
            email: Email
            password: Plain text password
            
        Returns:
            {
                "success": bool,
                "user_id": str,
                "message": str
            }
        """
        print(f"\n📝 Kullanıcı Kaydı: {email}")
        print("="*60)
        
        # 1. Email kontrolü (duplicate check)
        user_id = self.id_gen.generate_user_id(email)
        user_ref = self.db.collection(self.collections['users']).document(user_id)
        
        if user_ref.get().exists:
            print("❌ Email zaten kayıtlı!")
            return {
                "success": False,
                "message": "Email already registered"
            }
        
        # 2. Password hash (bcrypt)
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        hashed_password = hashed.decode('utf-8')
        
        print(f"   ✅ Password hashed (bcrypt)")
        
        # 3. User document oluştur
        user_doc = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "is_2fa_enabled": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "status": "active"
        }
        
        # 4. Hassas alanları şifrele
        encrypted_doc = self.encryption.encrypt_dict(
            user_doc,
            fields_to_encrypt=['hashed_password']
        )
        
        # 5. Firestore'a kaydet
        user_ref.set(encrypted_doc)
        
        print(f"   ✅ Kullanıcı kaydedildi: {user_id}")
        print("="*60)
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "User registered successfully"
        }
    
    def login(self, email: str, password: str) -> Dict:
        """
        Login Flow - Conditional Logic
        
        States:
        - PASSWORD_SUCCESS + NO_2FA → JWT returned
        - PASSWORD_SUCCESS + 2FA_ENABLED → 2FA_REQUIRED (202)
        - PASSWORD_FAILURE → 401 Unauthorized
        
        Args:
            email: User email
            password: Plain password
            
        Returns:
            {
                "success": bool,
                "requires_2fa": bool,
                "user_id": str (if 2FA required),
                "access_token": str (if success),
                "refresh_token": str (if success),
                "message": str
            }
        """
        print(f"\n🔐 Login Attempt: {email}")
        print("="*60)
        
        # 1. User ID hesapla
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. User'ı Firestore'dan getir
        user_ref = self.db.collection(self.collections['users']).document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print("   ❌ Kullanıcı bulunamadı")
            return {
                "success": False,
                "message": "Invalid credentials"
            }
        
        user_data = user_doc.to_dict()
        
        # 3. Encrypted password'u çöz
        decrypted_data = self.encryption.decrypt_dict(
            user_data,
            fields_to_decrypt=['hashed_password']
        )
        
        stored_hash = decrypted_data['hashed_password']
        
        # 4. Password verification (bcrypt)
        password_bytes = password.encode('utf-8')
        stored_hash_bytes = stored_hash.encode('utf-8')
        
        password_match = bcrypt.checkpw(password_bytes, stored_hash_bytes)
        
        if not password_match:
            print("   ❌ Yanlış şifre")
            return {
                "success": False,
                "message": "Invalid credentials"
            }
        
        print("   ✅ Password doğrulandı")
        
        # 5. 2FA kontrolü
        is_2fa_enabled = user_data.get('is_2fa_enabled', False)
        
        if is_2fa_enabled:
            print("   🔐 2FA gerekli (202 Accepted)")
            print("="*60)
            return {
                "success": False,
                "requires_2fa": True,
                "user_id": user_id,
                "email": email,
                "message": "2FA verification required"
            }
        
        # 6. 2FA yok → JWT token oluştur
        print("   ✅ 2FA yok, JWT oluşturuluyor...")
        tokens = self.jwt.create_token_pair(user_id, email)
        
        # 7. Last login güncelle
        user_ref.update({
            "last_login": datetime.utcnow()
        })
        
        # 8. Session'ı Firestore'a kaydet
        self._save_session(user_id, tokens['access_token'], tokens['refresh_token'])
        
        print("   ✅ Login başarılı!")
        print("="*60)
        
        return {
            "success": True,
            "requires_2fa": False,
            "access_token": tokens['access_token'],
            "refresh_token": tokens['refresh_token'],
            "token_type": tokens['token_type'],
            "message": "Login successful"
        }
    
    def verify_2fa_and_login(self, email: str, token: str) -> Dict:
        """
        2FA kod doğrulama ve JWT verme
        
        Args:
            email: User email
            token: 6-digit TOTP code
            
        Returns:
            {
                "success": bool,
                "access_token": str,
                "refresh_token": str,
                "message": str
            }
        """
        print(f"\n🔐 2FA Verification: {email}")
        print("="*60)
        
        # 1. TOTP token doğrula
        is_valid = self.twofa.verify_2fa_token(email, token)
        
        if not is_valid:
            print("   ❌ Geçersiz 2FA kodu")
            return {
                "success": False,
                "message": "Invalid 2FA code"
            }
        
        print("   ✅ 2FA doğrulandı")
        
        # 2. User ID al
        user_id = self.id_gen.generate_user_id(email)
        
        # 3. JWT token oluştur
        tokens = self.jwt.create_token_pair(user_id, email)
        
        # 4. Last login güncelle
        user_ref = self.db.collection(self.collections['users']).document(user_id)
        user_ref.update({
            "last_login": datetime.utcnow()
        })
        
        # 5. Session kaydet
        self._save_session(user_id, tokens['access_token'], tokens['refresh_token'])
        
        print("   ✅ Login başarılı (2FA ile)")
        print("="*60)
        
        return {
            "success": True,
            "access_token": tokens['access_token'],
            "refresh_token": tokens['refresh_token'],
            "token_type": tokens['token_type'],
            "message": "Login successful with 2FA"
        }
    
    def _save_session(self, user_id: str, access_token: str, refresh_token: str):
        """
        Session'ı Firestore'a şifreli kaydet
        
        Args:
            user_id: User ID
            access_token: JWT access token
            refresh_token: JWT refresh token
        """
        # Session ID oluştur
        session_id = self.id_gen.generate_session_id(user_id)
        
        # Session document
        session_doc = {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow(),
            "expires_at": None,  # JWT'nin kendi expiry'si var
            "is_active": True
        }
        
        # Token'ları şifrele
        encrypted_doc = self.encryption.encrypt_dict(
            session_doc,
            fields_to_encrypt=['access_token', 'refresh_token']
        )
        
        # Firestore'a kaydet
        session_ref = self.db.collection(self.collections['sessions']).document(session_id)
        session_ref.set(encrypted_doc)
        
        print(f"   💾 Session kaydedildi: {session_id[:16]}...")
    
    def verify_access_token(self, token: str) -> Optional[Dict]:
        """
        Access token doğrula (Protected route için)
        
        Args:
            token: JWT access token
            
        Returns:
            User payload veya None
        """
        payload = self.jwt.verify_token(token, expected_type="access")
        
        if not payload:
            return None
        
        return {
            "user_id": payload['sub'],
            "email": payload['email']
        }
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Refresh token ile yeni access token al
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            {"access_token": str} veya None
        """
        new_access = self.jwt.refresh_access_token(refresh_token)
        
        if not new_access:
            return None
        
        return {
            "access_token": new_access,
            "token_type": "bearer"
        }


# Test
if __name__ == "__main__":
    print("🧪 Auth Service Test - Sprint 4\n")
    
    # Initialize
    FirebaseConfig.initialize()
    auth = AuthService()
    
    test_email = "authtest@example.com"
    test_password = "SecurePassword123!"
    
    # Test 1: Register User
    print("🎯 TEST 1: REGISTER USER")
    print("="*70)
    result = auth.register_user("authtest", test_email, test_password)
    print(f"\n📋 Result: {result}")
    
    # Test 2: Login (No 2FA)
    print("\n\n🎯 TEST 2: LOGIN WITHOUT 2FA")
    print("="*70)
    result = auth.login(test_email, test_password)
    print(f"\n📋 Result:")
    print(f"   Success: {result['success']}")
    print(f"   Requires 2FA: {result.get('requires_2fa', False)}")
    if result['success']:
        print(f"   Access Token: {result['access_token'][:50]}...")
        print(f"   Refresh Token: {result['refresh_token'][:50]}...")
    
    # Test 3: Enable 2FA
    print("\n\n🎯 TEST 3: ENABLE 2FA")
    print("="*70)
    twofa_ops = Secure2FAOperations()
    twofa_result = twofa_ops.enable_2fa(test_email)
    print(f"   Secret: {twofa_result['secret']}")
    
    # Test 4: Login (With 2FA) - Should return 2FA_REQUIRED
    print("\n\n🎯 TEST 4: LOGIN WITH 2FA ENABLED")
    print("="*70)
    result = auth.login(test_email, test_password)
    print(f"\n📋 Result:")
    print(f"   Success: {result['success']}")
    print(f"   Requires 2FA: {result.get('requires_2fa', False)}")
    print(f"   User ID: {result.get('user_id', 'N/A')}")
    
    # Test 5: Verify 2FA and Complete Login
    print("\n\n🎯 TEST 5: VERIFY 2FA AND COMPLETE LOGIN")
    print("="*70)
    from totp_manager import TOTPManager
    totp = TOTPManager()
    current_token = totp.get_current_token(twofa_result['secret'])
    print(f"   Current TOTP: {current_token}")
    
    result = auth.verify_2fa_and_login(test_email, current_token)
    print(f"\n📋 Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Access Token: {result['access_token'][:50]}...")
    
    # Test 6: Verify Access Token (Protected Route)
    print("\n\n🎯 TEST 6: VERIFY ACCESS TOKEN")
    print("="*70)
    if result['success']:
        user_data = auth.verify_access_token(result['access_token'])
        print(f"   User Data: {user_data}")
    
    print("\n" + "="*70)
    print("✅ AUTH SERVICE TESTLERI TAMAMLANDI!")
    print("="*70)
