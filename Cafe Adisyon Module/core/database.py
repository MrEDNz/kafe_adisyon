import sqlite3
from pathlib import Path

class Database:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Veritabanını başlat ve bağlantı kur"""
        try:
            # Veritabanı dizini yoksa oluştur
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Sözlük benzeri erişim
            self._create_tables()
            print(f"Veritabanı başarıyla bağlandı: {self.db_path}")
        except Exception as e:
            print(f"Veritabanı bağlantı hatası: {str(e)}")
            raise

    def _create_tables(self):
        """Temel tabloları oluştur"""
        tables = [
            """CREATE TABLE IF NOT EXISTS masalar (
                masa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                masa_no INTEGER NOT NULL UNIQUE,
                isim TEXT,
                durum TEXT DEFAULT 'Boş'
            )""",
            # Diğer tablo tanımları...
        ]
        
        for table in tables:
            self.execute(table)

    def execute(self, query, params=(), fetch=False):
        """Sorgu çalıştır"""
        try:
            if not self.conn:
                self.connect()
                
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                if cursor.description and result:  # Sonuç ve sütun bilgisi kontrolü
                    columns = [col[0] for col in cursor.description]
                    return [dict(zip(columns, row)) for row in result]
                return []
                
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"Database error: {str(e)}")
            return [] if fetch else False

    def check_table_exists(self, table_name):
        """Belirtilen tablonun var olup olmadığını kontrol eder"""
        result = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
            fetch=True
        )
        return bool(result)

    def __del__(self):
        """Nesne silinirken bağlantıyı kapat"""
        if self.conn:
            self.conn.close()