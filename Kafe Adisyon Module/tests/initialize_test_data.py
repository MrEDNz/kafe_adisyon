from database import execute_query as db  # Değişiklik burada

def initialize_test_data():
    # Kullanıcılar
    users = [
        ("admin", "admin123", "admin"),
        ("user1", "user123", "user")
    ]
    
    # Masalar
    tables = [
        (1, 4),
        (2, 6),
        (3, 2),
        (4, 8)
    ]
    
    # Menü öğeleri
    menu_items = [
        ("Türk Kahvesi", "Sıcak İçecek", 15.0, 100),
        ("Çay", "Sıcak İçecek", 8.0, 200),
        ("Su", "İçecek", 5.0, 150),
        ("Hamburger", "Yemek", 65.0, 50)
    ]
    
    try:
        # Kullanıcıları ekle
        for user in users:
            db(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                user
            )
        
        # Masaları ekle
        for table in tables:
            db(
                "INSERT INTO tables (table_number, capacity) VALUES (?, ?)",
                table
            )
        
        # Menü öğelerini ekle
        for item in menu_items:
            db(
                "INSERT INTO menu_items (name, category, price, stock) VALUES (?, ?, ?, ?)",
                item
            )
        
        print("✅ Test verileri başarıyla yüklendi!")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    initialize_test_data()