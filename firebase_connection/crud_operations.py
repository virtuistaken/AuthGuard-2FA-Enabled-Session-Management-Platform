from firebase_config import FirebaseConfig
from data_schema import FirestoreSchema
from datetime import datetime

class FirestoreOperations:
    """Basit Firestore CRUD işlemleri"""
    
    def __init__(self):
        self.db = FirebaseConfig.get_db()
        self.collections = FirestoreSchema.get_collections()
    
    # CREATE
    def create_user(self, username: str, email: str, hashed_password: str) -> str:
        """Yeni kullanıcı oluştur"""
        user_doc = FirestoreSchema.user_document(username, email, hashed_password)
        
        # Firestore'a ekle
        doc_ref = self.db.collection(self.collections['users']).document()
        doc_ref.set(user_doc)
        
        print(f"✅ Kullanıcı oluşturuldu: {doc_ref.id}")
        return doc_ref.id
    
    # READ
    def get_user(self, user_id: str) -> dict:
        """Kullanıcıyı ID ile getir"""
        doc_ref = self.db.collection(self.collections['users']).document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            print(f"✅ Kullanıcı bulundu: {user_id}")
            return doc.to_dict()
        else:
            print(f"❌ Kullanıcı bulunamadı: {user_id}")
            return None
    
    def get_user_by_email(self, email: str) -> dict:
        """Email ile kullanıcı ara"""
        users_ref = self.db.collection(self.collections['users'])
        query = users_ref.where('email', '==', email).limit(1)
        
        docs = query.stream()
        for doc in docs:
            print(f"✅ Email ile kullanıcı bulundu: {email}")
            return {'id': doc.id, **doc.to_dict()}
        
        print(f"❌ Email bulunamadı: {email}")
        return None
    
    # UPDATE
    def update_user(self, user_id: str, data: dict) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        doc_ref = self.db.collection(self.collections['users']).document(user_id)
        
        # updated_at ekle
        data['updated_at'] = datetime.utcnow()
        
        doc_ref.update(data)
        print(f"✅ Kullanıcı güncellendi: {user_id}")
        return True
    
    # DELETE
    def delete_user(self, user_id: str) -> bool:
        """Kullanıcıyı sil"""
        doc_ref = self.db.collection(self.collections['users']).document(user_id)
        doc_ref.delete()
        print(f"✅ Kullanıcı silindi: {user_id}")
        return True
    
    # LIST
    def list_all_users(self, limit: int = 10):
        """Tüm kullanıcıları listele"""
        users_ref = self.db.collection(self.collections['users']).limit(limit)
        docs = users_ref.stream()
        
        users = []
        for doc in docs:
            users.append({'id': doc.id, **doc.to_dict()})
        
        print(f"✅ {len(users)} kullanıcı bulundu")
        return users


# Test
if __name__ == "__main__":
    print("🧪 Firestore CRUD Test\n")
    
    # Initialize
    FirebaseConfig.initialize()
    ops = FirestoreOperations()
    
    # CREATE
    print("1️⃣ CREATE - Kullanıcı oluştur")
    user_id = ops.create_user(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$hashed_password_here"
    )
    
    # READ
    print("\n2️⃣ READ - Kullanıcıyı getir")
    user = ops.get_user(user_id)
    if user:
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
    
    # UPDATE
    print("\n3️⃣ UPDATE - Kullanıcıyı güncelle")
    ops.update_user(user_id, {
        "last_login": datetime.utcnow(),
        "status": "active"
    })
    
    # READ by Email
    print("\n4️⃣ READ by Email")
    user = ops.get_user_by_email("test@example.com")
    if user:
        print(f"Found user: {user['username']}")
    
    # LIST
    print("\n5️⃣ LIST - Tüm kullanıcılar")
    users = ops.list_all_users(limit=5)
    for i, user in enumerate(users, 1):
        print(f"   {i}. {user['username']} ({user['email']})")
    
    # DELETE (dikkatli kullan!)
    # print("\n6️⃣ DELETE - Kullanıcıyı sil")
    # ops.delete_user(user_id)
