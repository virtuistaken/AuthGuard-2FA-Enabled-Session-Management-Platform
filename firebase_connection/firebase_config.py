import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:
    """Firebase bağlantı konfigürasyonu"""
    
    _db = None
    
    @classmethod
    def initialize(cls):
        """Firebase'i başlat"""
        if not firebase_admin._apps:
            # Service account key dosyası yolu
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
            
            # Firebase credentials
            cred = credentials.Certificate(cred_path)
            
            # Firebase uygulamasını başlat
            firebase_admin.initialize_app(cred)
            
            print(" Firebase bağlantısı başarılı!")
        
        # Firestore database referansı
        cls._db = firestore.client()
        return cls._db
    
    @classmethod
    def get_db(cls):
        """Database referansını al"""
        if cls._db is None:
            cls._db = cls.initialize()
        return cls._db

# Test
if __name__ == "__main__":
    try:
        db = FirebaseConfig.initialize()
        print(" Firestore database hazır!")
        print(f"Database instance: {db}")
    except Exception as e:
        print(f" Hata: {e}")
