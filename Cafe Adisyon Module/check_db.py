import sqlite3
from config import DB_PATH

def check_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabloları listele
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Veritabanı Tabloları:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Tablo sütunlarını göster
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print(f"  Sütunlar: {[col[1] for col in columns]}")
            
        conn.close()
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    check_database()