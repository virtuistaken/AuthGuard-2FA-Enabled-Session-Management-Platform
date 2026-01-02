from firebase_config import FirebaseConfig
from data_schema import FirestoreSchema
from encryption import EncryptionModule
from md5_docid import MD5DocIDGenerator
from totp_manager import TOTPManager
from datetime import datetime
from typing import Dict, Optional

class Secure2FAOperations:
    """
    2FA operasyonları - TOTP entegreli
    HAFTA 3: Sprint 3 - 2FA Core Implementation
    
    Özellikler:
    - TOTP secret üretimi ve şifreleme
    - QR kod oluşturma
    - 6-digit kod doğrulama
    - Clock drift toleransı (±30 saniye)
    """
    
    def __init__(self):
        self.db = FirebaseConfig.get_db()
        self.collections = FirestoreSchema.get_collections()
        self.encryption = EncryptionModule()
        self.id_gen = MD5DocIDGenerator()
        self.totp = TOTPManager(issuer_name="AuthGuard")
    
    def enable_2fa(self, email: str) -> Dict[str, str]:
        """
        Kullanıcı için 2FA aktif et
        
        Args:
            email: Kullanıcı email
            
        Returns:
            {
                'user_id': str,
                'secret': str (encrypted),
                'qr_code': str (base64 PNG),
                'manual_entry_key': str (plain for display)
            }
        """
        print(f"\n🔐 2FA Aktifleştirme Başlatıldı: {email}")
        print("="*60)
        
        # 1. User ID al
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. TOTP secret üret
        totp_secret = self.totp.generate_secret()
        print(f"   ✅ Secret oluşturuldu: {totp_secret[:8]}...")
        
        # 3. QR kod oluştur
        qr_code = self.totp.generate_qr_code(email, totp_secret)
        print(f"   ✅ QR kod oluşturuldu")
        
        # 4. 2FA document hazırla
        tfa_doc = FirestoreSchema.two_factor_auth_document(
            user_id=user_id,
            secret_key=totp_secret
        )
        
        # 5. Secret'ı şifrele
        encrypted_doc = self.encryption.encrypt_dict(
            tfa_doc,
            fields_to_encrypt=['secret_key']
        )
        
        # 6. Firestore'a kaydet
        tfa_id = self.id_gen.generate_2fa_id(user_id)
        doc_ref = self.db.collection(self.collections['two_factor_auth']).document(tfa_id)
        doc_ref.set(encrypted_doc)
        
        print(f"   ✅ Şifreli secret Firestore'a kaydedildi")
        print(f"   📍 Document ID: {tfa_id}")
        
        # 7. User'ın is_2fa_enabled flag'ini güncelle
        user_ref = self.db.collection(self.collections['users']).document(user_id)
        user_ref.update({
            'is_2fa_enabled': True,
            'updated_at': datetime.utcnow()
        })
        
        print(f"\n✅ 2FA başarıyla aktifleştirildi!")
        print("="*60)
        
        return {
            'user_id': user_id,
            'secret': totp_secret,  # Frontend için (şifrelenmeden)
            'qr_code': qr_code,
            'manual_entry_key': totp_secret  # Manuel giriş için
        }
    
    def verify_2fa_token(self, email: str, token: str) -> bool:
        """
        6-digit TOTP kodunu doğrula
        
        Args:
            email: Kullanıcı email
            token: 6-digit kod
            
        Returns:
            True eğer kod geçerliyse
        """
        print(f"\n🔍 2FA Token Doğrulama: {email}")
        print("="*60)
        
        # 1. User ID al
        user_id = self.id_gen.generate_user_id(email)
        tfa_id = self.id_gen.generate_2fa_id(user_id)
        
        # 2. 2FA secret'ını getir
        doc_ref = self.db.collection(self.collections['two_factor_auth']).document(tfa_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print("   ❌ 2FA kaydı bulunamadı")
            return False
        
        # 3. Secret'ı çöz
        encrypted_data = doc.to_dict()
        decrypted_data = self.encryption.decrypt_dict(
            encrypted_data,
            fields_to_decrypt=['secret_key']
        )
        
        secret = decrypted_data['secret_key']
        print(f"   ✅ Secret çözüldü: {secret[:8]}...")
        
        # 4. Token'ı doğrula (±30 saniye tolerans)
        is_valid = self.totp.verify_token(secret, token, window=1)
        
        if is_valid:
            # 5. last_used timestamp'i güncelle
            doc_ref.update({
                'last_used': datetime.utcnow()
            })
            print(f"   ✅ Token geçerli!")
            print(f"   ⏰ Kalan süre: {self.totp.get_time_remaining()}s")
        else:
            print(f"   ❌ Token geçersiz!")
        
        print("="*60)
        return is_valid
    
    def disable_2fa(self, email: str) -> bool:
        """
        2FA'yı devre dışı bırak
        
        Args:
            email: Kullanıcı email
            
        Returns:
            True eğer başarılıysa
        """
        print(f"\n🚫 2FA Devre Dışı Bırakılıyor: {email}")
        print("="*60)
        
        # 1. User ID al
        user_id = self.id_gen.generate_user_id(email)
        
        # 2. 2FA document'i sil
        tfa_id = self.id_gen.generate_2fa_id(user_id)
        doc_ref = self.db.collection(self.collections['two_factor_auth']).document(tfa_id)
        doc_ref.delete()
        
        print(f"   ✅ 2FA kaydı silindi")
        
        # 3. User'ın flag'ini güncelle
        user_ref = self.db.collection(self.collections['users']).document(user_id)
        user_ref.update({
            'is_2fa_enabled': False,
            'updated_at': datetime.utcnow()
        })
        
        print(f"   ✅ User flag'i güncellendi")
        print("="*60)
        
        return True
    
    def get_2fa_status(self, email: str) -> Dict:
        """
        Kullanıcının 2FA durumunu getir
        
        Args:
            email: Kullanıcı email
            
        Returns:
            {
                'is_enabled': bool,
                'last_used': datetime or None,
                'created_at': datetime or None
            }
        """
        user_id = self.id_gen.generate_user_id(email)
        tfa_id = self.id_gen.generate_2fa_id(user_id)
        
        doc_ref = self.db.collection(self.collections['two_factor_auth']).document(tfa_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return {
                'is_enabled': False,
                'last_used': None,
                'created_at': None
            }
        
        data = doc.to_dict()
        return {
            'is_enabled': data.get('is_enabled', False),
            'last_used': data.get('last_used'),
            'created_at': data.get('created_at')
        }


# Test
if __name__ == "__main__":
    print("🧪 Secure 2FA Operations Test - Sprint 3\n")
    
    # Initialize
    FirebaseConfig.initialize()
    ops = Secure2FAOperations()
    
    test_email = "2fa-test@example.com"
    
    # Test 1: 2FA Aktifleştirme
    print("\n" + "🎯 TEST 1: 2FA ENABLE")
    print("="*70)
    result = ops.enable_2fa(test_email)
    
    print(f"\n📋 Sonuç:")
    print(f"   User ID: {result['user_id']}")
    print(f"   Secret: {result['secret']}")
    print(f"   QR Code: {result['qr_code'][:80]}...")
    print(f"\n💡 Bu QR kodu Google Authenticator'da tarayın!")
    
    # Test 2: Token Alma (simülasyon)
    print("\n\n" + "🎯 TEST 2: GET CURRENT TOKEN")
    print("="*70)
    totp_mgr = TOTPManager()
    current_token = totp_mgr.get_current_token(result['secret'])
    print(f"   📱 Şu anki token: {current_token}")
    print(f"   ⏰ Kalan süre: {totp_mgr.get_time_remaining()}s")
    
    # Test 3: Token Doğrulama (doğru kod)
    print("\n\n" + "🎯 TEST 3: VERIFY VALID TOKEN")
    print("="*70)
    is_valid = ops.verify_2fa_token(test_email, current_token)
    print(f"   ✅ Sonuç: {'BAŞARILI' if is_valid else 'BAŞARISIZ'}")
    
    # Test 4: Token Doğrulama (yanlış kod)
    print("\n\n" + "🎯 TEST 4: VERIFY INVALID TOKEN")
    print("="*70)
    is_valid = ops.verify_2fa_token(test_email, "000000")
    print(f"   ✅ Sonuç: {'BAŞARISIZ (beklenen)' if not is_valid else 'HATA!'}")
    
    # Test 5: 2FA Durumu
    print("\n\n" + "🎯 TEST 5: GET 2FA STATUS")
    print("="*70)
    status = ops.get_2fa_status(test_email)
    print(f"   Durum: {status}")
    
    # Test 6: 2FA Devre Dışı Bırakma (opsiyonel - yorumdan çıkar)
    # print("\n\n" + "🎯 TEST 6: DISABLE 2FA")
    # print("="*70)
    # ops.disable_2fa(test_email)
    
    print("\n\n" + "="*70)
    print("✅ HAFTA 3 TESTLERI TAMAMLANDI!")
    print("="*70)
    print("\n📱 Google Authenticator'da QR kodu tarayın ve kodu deneyin!")
