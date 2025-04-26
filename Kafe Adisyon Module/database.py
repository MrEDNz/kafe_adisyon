# database.py
import sqlite3
from contextlib import contextmanager

DATABASE_NAME = "cafe.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query: str, params: tuple = (), fetch: bool = False):
    """Tüm veritabanı işlemleri için ortak fonksiyon (db_execute olarak da kullanılabilir)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return [dict(row) for row in cursor.fetchall()]
        conn.commit()

# Alias tanımlaması (db_execute ile execute_query aynı işlevi görecek)
db_execute = execute_query

def initialize_database():
    tables = [
        """CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',
            capacity INTEGER NOT NULL)""",

        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL)""",
        
        """CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'available',
            capacity INTEGER NOT NULL)""",
            
        """CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0)""",
            
        """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            total_amount REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (table_id) REFERENCES tables(id))""",
            
        """CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id))"""
    ]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for table in tables:
            execute_query(table)
        conn.commit()

# Veritabanı başlatma
initialize_database()