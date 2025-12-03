from firebase_config import FirebaseConfig
from data_schema import FirestoreSchema
from encryption import EncryptionModule
from md5_docid import MD5DocIDGenerator
from datetime import datetime

class SecureFirestoreOperations:
    """
    Şifreli veri yükleme ve MD5 doc_id ile Firestore işlemleri
    HAFTA 2 İÇİN
    """
    
    def __init__(self):
        self.db = FirebaseConfig.get_db()
        self.collections = FirestoreSchema.get_collections()
        self.encryption = EncryptionModule()
        self.id_gen = MD5DocIDGenerator()
    
    def create_secure_user(self, username: str, email: str, password: str) -> str:
        """
        Şifreli kullanıcı oluştur + MD5 doc_id
        
        Args:
            username: Kullanıcı adı
            email: Email
            password: Şifre (plain text - şifrelenecek)
            
        Returns:
            User document ID (MD5 hash of email)
        """
        # 1. MD5 doc_id oluştur
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. User document hazırla
        user_doc = FirestoreSchema.user_document(
            username=username,
            email=email,
            hashed_password=password  # Normalde bcrypt ile hash'lenmeli
        )
        
        # 3. Hassas alanları şifrele
        encrypted_doc = self.encryption.encrypt_dict(
            user_doc,
            fields_to_encrypt=['hashed_password']
        )
        
        # 4. Firestore'a kaydet (MD5 ID ile)
        doc_ref = self.db.collection(self.collections['users']).document(user_id)
        doc_ref.set(encrypted_doc)
        
        print(f"✅ Şifreli kullanıcı oluşturuldu")
        print(f"   Email: {email}")
        print(f"   Doc ID: {user_id}")
        
        return user_id
    
    def get_secure_user(self, email: str) -> dict:
        """
        Şifreli kullanıcıyı getir ve çöz
        
        Args:
            email: Kullanıcı email
            
        Returns:
            Çözülmüş user data
        """
        # 1. MD5 doc_id hesapla
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. Firestore'dan getir
        doc_ref = self.db.collection(self.collections['users']).document(user_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"❌ Kullanıcı bulunamadı: {email}")
            return None
        
        # 3. Şifreyi çöz
        encrypted_data = doc.to_dict()
        decrypted_data = self.encryption.decrypt_dict(
            encrypted_data,
            fields_to_decrypt=['hashed_password']
        )
        
        print(f"✅ Kullanıcı bulundu ve şifresi çözüldü: {email}")
        
        return {'id': user_id, **decrypted_data}
    
    def create_secure_session(self, email: str, access_token: str, refresh_token: str) -> str:
        """
        Şifreli session oluştur + MD5 doc_id
        
        Args:
            email: Kullanıcı email
            access_token: JWT access token
            refresh_token: JWT refresh token
            
        Returns:
            Session document ID
        """
        # 1. User ID al
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. Session ID oluştur (user_id + timestamp)
        timestamp = datetime.utcnow().isoformat()
        session_id = self.id_gen.generate_session_id(user_id, timestamp)
        
        # 3. Session document hazırla
        session_doc = FirestoreSchema.session_document(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # 4. Token'ları şifrele
        encrypted_doc = self.encryption.encrypt_dict(
            session_doc,
            fields_to_encrypt=['access_token', 'refresh_token']
        )
        
        # 5. Firestore'a kaydet
        doc_ref = self.db.collection(self.collections['sessions']).document(session_id)
        doc_ref.set(encrypted_doc)
        
        print(f"✅ Şifreli session oluşturuldu")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id}")
        
        return session_id
    
    def create_secure_2fa(self, email: str, totp_secret: str) -> str:
        """
        Şifreli 2FA secret kaydet + MD5 doc_id
        
        Args:
            email: Kullanıcı email
            totp_secret: TOTP secret key
            
        Returns:
            2FA document ID (user_id ile aynı)
        """
        # 1. User ID al
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. 2FA document hazırla
        tfa_doc = FirestoreSchema.two_factor_auth_document(
            user_id=user_id,
            secret_key=totp_secret
        )
        
        # 3. Secret'ı şifrele
        encrypted_doc = self.encryption.encrypt_dict(
            tfa_doc,
            fields_to_encrypt=['secret_key']
        )
        
        # 4. Firestore'a kaydet (2FA ID = user_id)
        tfa_id = self.id_gen.generate_2fa_id(user_id)
        doc_ref = self.db.collection(self.collections['two_factor_auth']).document(tfa_id)
        doc_ref.set(encrypted_doc)
        
        print(f"✅ Şifreli 2FA secret kaydedildi")
        print(f"   User ID: {user_id}")
        print(f"   2FA Doc ID: {tfa_id}")
        
        return tfa_id
    
    def get_secure_2fa(self, email: str) -> dict:
        """
        Şifreli 2FA secret'ı getir ve çöz
        
        Args:
            email: Kullanıcı email
            
        Returns:
            Çözülmüş 2FA data
        """
        # 1. User ID al
        user_id = self.id_gen.generate_user_id(email)
        tfa_id = self.id_gen.generate_2fa_id(user_id)
        
        # 2. Firestore'dan getir
        doc_ref = self.db.collection(self.collections['two_factor_auth']).document(tfa_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"❌ 2FA bulunamadı: {email}")
            return None
        
        # 3. Secret'ı çöz
        encrypted_data = doc.to_dict()
        decrypted_data = self.encryption.decrypt_dict(
            encrypted_data,
            fields_to_decrypt=['secret_key']
        )
        
        print(f"✅ 2FA secret bulundu ve çözüldü: {email}")
        
        return {'id': tfa_id, **decrypted_data}


# Test
if __name__ == "__main__":
    print("🔐 Secure Firestore Operations Test\n")
    
    # Initialize
    FirebaseConfig.initialize()
    secure_ops = SecureFirestoreOperations()
    
    test_email = "secure@example.com"
    
    # Test 1: Secure User Creation
    print("="*60)
    print("1️⃣ CREATE SECURE USER")
    print("="*60)
    user_id = secure_ops.create_secure_user(
        username="secureuser",
        email=test_email,
        password="MySecretPassword123!"
    )
    
    # Test 2: Get Secure User
    print("\n" + "="*60)
    print("2️⃣ GET SECURE USER")
    print("="*60)
    user = secure_ops.get_secure_user(test_email)
    if user:
        print(f"\n📋 User Data:")
        print(f"   ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Password: {user['hashed_password']}")  # Çözülmüş
    
    # Test 3: Secure Session
    print("\n" + "="*60)
    print("3️⃣ CREATE SECURE SESSION")
    print("="*60)
    session_id = secure_ops.create_secure_session(
        email=test_email,
        access_token="jwt.access.token.here",
        refresh_token="jwt.refresh.token.here"
    )
    
    # Test 4: Secure 2FA
    print("\n" + "="*60)
    print("4️⃣ CREATE SECURE 2FA")
    print("="*60)
    tfa_id = secure_ops.create_secure_2fa(
        email=test_email,
        totp_secret="JBSWY3DPEHPK3PXP"
    )
    
    # Test 5: Get Secure 2FA
    print("\n" + "="*60)
    print("5️⃣ GET SECURE 2FA")
    print("="*60)
    tfa = secure_ops.get_secure_2fa(test_email)
    if tfa:
        print(f"\n📋 2FA Data:")
        print(f"   ID: {tfa['id']}")
        print(f"   User ID: {tfa['user_id']}")
        print(f"   Secret: {tfa['secret_key']}")  # Çözülmüş
        print(f"   Enabled: {tfa['is_enabled']}")
    
    print("\n" + "="*60)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*60)
