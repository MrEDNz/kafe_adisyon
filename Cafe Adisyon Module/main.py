import tkinter as tk
from tkinter import ttk
from config import configure_styles, DB_PATH, THEME, WINDOW_TITLE, WINDOW_SIZE
from core.database import Database
from modules.masa import MasaModule
from modules.urun import UrunModule
from modules.musteri import MusteriModule
from modules.siparis import SiparisModule
from modules.rapor import RaporModule

class CafeAdisyonProgrami:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # Stil ayarlarını yükle
        configure_styles()
        
        try:
            style = ttk.Style()
            style.theme_use(THEME)
        except Exception as e:
            print(f"Tema yükleme hatası: {str(e)}")
        
        # Veritabanı bağlantısı (hata yönetimi ile)
        try:
            self.db = Database(DB_PATH)
            self._check_database()
            if not self._verify_database():  # Doğrulama başarısızsa
                return  # Hemen çık
            
        except Exception as e:
            tk.messagebox.showerror(
                "Kritik Hata", 
                f"Veritabanı bağlantısı kurulamadı:\n{str(e)}"
            )
            self.root.destroy()
            return
        
        # Notebook (Tab) oluşturma
        try:
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill=tk.BOTH, expand=True)
            
            # Modülleri oluştur
            self._initialize_modules()
            
            # Pencere boyutlandırma
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)
            
        except Exception as e:
            tk.messagebox.showerror(
                "Başlatma Hatası",
                f"Program başlatılırken hata oluştu:\n{str(e)}"
            )
            self.root.destroy()
    
    def _check_database(self):
        """Temel veritabanı kontrollerini yapar ve örnek veri ekler"""
        try:
            # Önce mevcut tabloları sil (varsa)
            self.db.execute("DROP TABLE IF EXISTS masalar")
            self.db.execute("DROP TABLE IF EXISTS urunler")
            self.db.execute("DROP TABLE IF EXISTS siparisler")
            
            # Yeni tabloları oluştur
            self.db.execute("""
            CREATE TABLE masalar (
                masa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                masa_no INTEGER NOT NULL UNIQUE,
                isim TEXT,
                durum TEXT DEFAULT 'Boş'
            )""")
            
            self.db.execute("""
            CREATE TABLE urunler (
                urun_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                fiyat REAL NOT NULL
            )""")
            
            self.db.execute("""
            CREATE TABLE siparisler (
                siparis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                masa_id INTEGER NOT NULL,
                urun_id INTEGER NOT NULL,
                adet INTEGER NOT NULL,
                durum TEXT DEFAULT 'Hazırlanıyor',
                FOREIGN KEY(masa_id) REFERENCES masalar(masa_id),
                FOREIGN KEY(urun_id) REFERENCES urunler(urun_id)
            )""")

            self.db.execute("""
            CREATE TABLE IF NOT EXISTS kategoriler (
                kategori_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL
            )""")
            
            self.db.execute("""
            CREATE TABLE IF NOT EXISTS musteriler (
                musteri_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                telefon TEXT,
                eposta TEXT
            )""")
            
            # Örnek verileri ekle
            sample_masalar = [
                (1, "Köşe Masa", "Boş"),
                (2, "Salon Masa", "Boş"),
                (3, "Bahçe Masa", "Boş")
            ]
            for no, isim, durum in sample_masalar:
                self.db.execute(
                    "INSERT INTO masalar (masa_no, isim, durum) VALUES (?, ?, ?)",
                    (no, isim, durum)
                )
                
            print("Veritabanı başarıyla oluşturuldu ve örnek veriler eklendi.")
            
        except Exception as e:
            raise RuntimeError(f"Veritabanı oluşturulamadı: {str(e)}")

    def _initialize_modules(self):
        """Tüm modülleri başlatır (main.py'ye eklenecek)"""
        self.moduller = {
            "Masalar": MasaModule(self.notebook, self.db),
            "Ürünler": UrunModule(self.notebook, self.db),
            "Müşteriler": MusteriModule(self.notebook, self.db),
            "Siparişler": SiparisModule(self.notebook, self.db),
            "Raporlar": RaporModule(self.notebook, self.db)
        }
        
        for name, module in self.moduller.items():
            self.notebook.add(module.frame, text=name)

    def _verify_database(self):
        """Veritabanı yapısını ve temel tabloları doğrular"""
        required_tables = {
            'masalar': ['masa_id', 'masa_no', 'isim', 'durum'],
            'urunler': ['urun_id', 'ad', 'fiyat'],
            'siparisler': ['siparis_id', 'masa_id', 'urun_id', 'adet', 'durum']
        }
        
        try:
            for table, columns in required_tables.items():
                # Tablo var mı kontrolü
                if not self.db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table,),
                    fetch=True
                ):
                    raise RuntimeError(f"Gerekli tablo bulunamadı: {table}")
                
                # Sütunlar doğru mu kontrolü
                table_info = self.db.execute(f"PRAGMA table_info({table})", fetch=True)
                if not table_info:  # Tablo boş olabilir
                    continue
                    
                existing_columns = [col['name'] for col in table_info]
                
                for col in columns:
                    if col not in existing_columns:
                        raise RuntimeError(f"{table} tablosunda gerekli sütun bulunamadı: {col}")
                        
            print("Veritabanı doğrulaması başarılı!")
            return True
            
        except Exception as e:
            tk.messagebox.showerror(
                "Veritabanı Hatası",
                f"Veritabanı yapısı doğrulanamadı:\n{str(e)}\n\n"
                "Program kapatılacak."
            )
            self.root.destroy()
            return False
        
if __name__ == "__main__":
    root = tk.Tk()
    
    try:
        app = CafeAdisyonProgrami(root)
        
        # Veritabanı bağlantısı başarılıysa ve pencere yok edilmemişse
        if hasattr(app, 'db') and app.db and root.winfo_exists():
            root.mainloop()
            
    except Exception as e:
        # Hata durumunda kullanıcıyı bilgilendir
        error_msg = f"Program başlatılamadı:\n{str(e)}"
        print(error_msg)  # Terminale yazdır
        try:
            tk.messagebox.showerror("Kritik Hata", error_msg)
        except:
            pass  # GUI başlatılamazsa devam et
        
        try:
            root.destroy()  # Pencereyi kapatmayı dene
        except:
            pass  # Pencere oluşmamışsa hata verme