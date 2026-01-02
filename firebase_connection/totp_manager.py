import pyotp
import qrcode
import io
import base64
from datetime import datetime
from typing import Tuple, Optional, Dict

class TOTPManager:
    """
    TOTP (Time-based One-Time Password) yönetimi
    RFC 6238 standardına uygun
    HAFTA 3 - 2FA Core Implementation
    """
    
    def __init__(self, issuer_name: str = "AuthGuard"):
        """
        Args:
            issuer_name: Authenticator uygulamasında görünecek isim
        """
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        """
        256-bit güvenli TOTP secret oluştur
        
        Returns:
            Base32-encoded secret key (32 karakter)
        """
        # pyotp otomatik olarak güvenli random secret üretir
        secret = pyotp.random_base32()
        
        print(f"✅ TOTP secret oluşturuldu: {secret[:8]}...")
        return secret
    
    def generate_provisioning_uri(self, email: str, secret: str) -> str:
        """
        otpauth:// URI oluştur (QR kod için)
        
        Args:
            email: Kullanıcı email
            secret: TOTP secret key
            
        Returns:
            otpauth:// format URI
        """
        totp = pyotp.TOTP(secret)
        
        # Google Authenticator uyumlu URI
        uri = totp.provisioning_uri(
            name=email,
            issuer_name=self.issuer_name
        )
        
        print(f"✅ Provisioning URI oluşturuldu")
        return uri
    
    def generate_qr_code(self, email: str, secret: str) -> str:
        """
        QR kod oluştur ve base64 string olarak döndür
        
        Args:
            email: Kullanıcı email
            secret: TOTP secret key
            
        Returns:
            Base64-encoded PNG image
        """
        # Provisioning URI al
        uri = self.generate_provisioning_uri(email, secret)
        
        # QR kod oluştur
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # PNG image oluştur
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Memory'de tutmak için BytesIO kullan
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Base64'e encode et
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print(f"✅ QR kod oluşturuldu ({len(img_base64)} bytes)")
        return f"data:image/png;base64,{img_base64}"
    
    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        6-digit TOTP kodunu doğrula
        
        Args:
            secret: Kullanıcının TOTP secret'ı
            token: Kullanıcının girdiği 6-digit kod
            window: Zaman toleransı (±30 saniye)
            
        Returns:
            True eğer kod geçerliyse
        """
        try:
            totp = pyotp.TOTP(secret)
            
            # Token'ı doğrula (30 saniye window ile)
            is_valid = totp.verify(token, valid_window=window)
            
            if is_valid:
                print(f"✅ TOTP token doğrulandı")
            else:
                print(f"❌ Geçersiz TOTP token")
            
            return is_valid
            
        except Exception as e:
            print(f"❌ TOTP doğrulama hatası: {e}")
            return False
    
    def get_current_token(self, secret: str) -> str:
        """
        Şu anki geçerli token'ı al (test için)
        
        Args:
            secret: TOTP secret
            
        Returns:
            6-digit kod
        """
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def get_time_remaining(self) -> int:
        """
        Mevcut token için kalan süreyi saniye cinsinden döndür
        
        Returns:
            Kalan saniye (0-30 arası)
        """
        import time
        return 30 - int(time.time() % 30)


# Test
if __name__ == "__main__":
    print("🔐 TOTP Manager Test\n")
    print("="*60)
    
    # Initialize
    totp_mgr = TOTPManager(issuer_name="AuthGuard")
    
    # Test 1: Secret Generation
    print("\n1️⃣ SECRET GENERATION")
    print("="*60)
    secret = totp_mgr.generate_secret()
    print(f"Secret: {secret}")
    print(f"Length: {len(secret)} characters")
    
    # Test 2: Provisioning URI
    print("\n2️⃣ PROVISIONING URI")
    print("="*60)
    email = "test@example.com"
    uri = totp_mgr.generate_provisioning_uri(email, secret)
    print(f"URI: {uri[:80]}...")
    
    # Test 3: QR Code Generation
    print("\n3️⃣ QR CODE GENERATION")
    print("="*60)
    qr_code = totp_mgr.generate_qr_code(email, secret)
    print(f"QR Code (base64): {qr_code[:100]}...")
    print(f"Total length: {len(qr_code)} characters")
    
    # Test 4: Token Generation
    print("\n4️⃣ TOKEN GENERATION")
    print("="*60)
    current_token = totp_mgr.get_current_token(secret)
    print(f"Current Token: {current_token}")
    print(f"Time Remaining: {totp_mgr.get_time_remaining()} seconds")
    
    # Test 5: Token Verification
    print("\n5️⃣ TOKEN VERIFICATION")
    print("="*60)
    
    # Doğru token
    is_valid = totp_mgr.verify_token(secret, current_token)
    print(f"Valid Token Test: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    
    # Yanlış token
    is_valid = totp_mgr.verify_token(secret, "000000")
    print(f"Invalid Token Test: {'✅ PASSED' if not is_valid else '❌ FAILED'}")
    
    # Test 6: Time Window Test
    print("\n6️⃣ TIME WINDOW TEST")
    print("="*60)
    print("⏳ 30 saniye içinde aynı token geçerli olmalı...")
    import time
    time.sleep(2)
    is_still_valid = totp_mgr.verify_token(secret, current_token)
    print(f"Same Token After 2s: {'✅ VALID' if is_still_valid else '❌ INVALID'}")
    
    print("\n" + "="*60)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*60)
    print("\n📱 QR kodu Google Authenticator ile tarayabilirsiniz!")
    print(f"🔑 Manuel giriş için secret: {secret}")
