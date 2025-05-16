# database.py

import sqlite3
import sys
from tkinter import messagebox
from datetime import datetime, date, timedelta
import constants
import os # Arşiv dosyası oluşturmak için
import shutil # Dosya kopyalama için

class DatabaseManager:
    def __init__(self, db_name=constants.DB_NAME):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect_db()
        self._create_tables()
        self._add_default_data()

    def _connect_db(self):
        """SQLite veritabanı bağlantısını kurar."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            # Sorgu sonuçlarına sütun isimleriyle erişmek için
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print("Veritabanı bağlantısı başarılı.")
        except sqlite3.Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Veritabanına bağlanılamadı: {e}")
            sys.exit() # Bağlantı kurulamıyorsa uygulamayı sonlandır

    def close(self):
        """Veritabanı bağlantısını kapatır."""
        if self.conn:
            self.conn.close()
            print("Veritabanı bağlantısı kapatıldı.")

    def _create_tables(self):
        """Gerekli veritabanı tablolarını oluşturur."""
        try:
            # Masalar tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS masalar (
                    masa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    masa_no INTEGER UNIQUE NOT NULL,
                    durum TEXT DEFAULT 'Boş', -- 'Boş', 'Dolu', 'Ödeme Bekliyor', 'Geçikmiş'
                    aktif_siparis_id INTEGER, -- O anki aktif siparişin ID'si
                    guncel_toplam REAL DEFAULT 0.0, -- İskonto ve parçalı ödeme sonrası kalan net tutar
                    iskonto REAL DEFAULT 0.0, -- Uygulanan toplam iskonto
                    FOREIGN KEY (aktif_siparis_id) REFERENCES siparis_gecmisi(siparis_id)
                );
            """)

            # Kategoriler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS kategoriler (
                    kategori_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adi TEXT UNIQUE NOT NULL
                );
            """)

            # Ürünler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS urunler (
                    urun_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adi TEXT UNIQUE NOT NULL,
                    fiyat REAL NOT NULL,
                    kategori_id INTEGER,
                    aktif_durumu INTEGER DEFAULT 1, -- 1: Aktif, 0: Pasif (BOOLEAN SQLite'da INTEGER'dır)
                    hizli_satis_sirasi INTEGER, -- Hızlı satış ekranındaki sıralama (0: görünmez)
                    FOREIGN KEY (kategori_id) REFERENCES kategoriler(kategori_id) ON DELETE SET NULL
                );
            """)

            # Sipariş Geçmişi tablosu (Adisyonlar)
            # musteri_id eklendi, odenen_tutar eklendi, son_islem_zamani eklendi
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS siparis_gecmisi (
                    siparis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    masa_no INTEGER NOT NULL,
                    acilis_zamani TEXT NOT NULL,
                    kapanis_zamani TEXT,
                    durum TEXT DEFAULT 'Açık', -- 'Açık', 'Kapandı', 'İptal Edildi'
                    toplam_tutar REAL DEFAULT 0.0, -- Kapanış anındaki toplam brüt tutar
                    iskonto REAL DEFAULT 0.0, -- Kapanış anındaki toplam iskonto
                    odenen_tutar REAL DEFAULT 0.0, -- Yapılan parçalı ödemeler dahil toplam ödenen tutar
                    odeme_yontemi TEXT, -- 'Nakit', 'Kart', 'Müşteri Bakiyesi' vb. (Son ödeme veya ana ödeme yöntemi)
                    son_islem_zamani TEXT, -- Masa durumu takibi için son ürün ekleme/ödeme zamanı
                    musteri_id INTEGER, -- İlişkilendirilen müşteri
                    FOREIGN KEY (masa_no) REFERENCES masalar(masa_no) ON DELETE SET NULL,
                    FOREIGN KEY (musteri_id) REFERENCES musteriler(musteri_id) ON DELETE SET NULL
                );
            """)

            # Sipariş Detayları tablosu (Adisyondaki ürünler)
            # Yeni sütun eklendi: ekleme_zamani
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS siparis_detaylari (
                    detay_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    siparis_id INTEGER NOT NULL,
                    urun_id INTEGER, -- Bağlantılı ürün (ON DELETE SET NULL)
                    urun_adi TEXT NOT NULL, -- Ürün adı (raporlama kolaylığı ve tutarlılık için saklanıyor)
                    miktar REAL NOT NULL,
                    birim_fiyat REAL NOT NULL, -- Ürünün sipariş anındaki fiyatı
                    tutar REAL NOT NULL, -- miktar * birim_fiyat
                    kategori_id INTEGER, -- Ürün kategori ID'si (raporlama kolaylığı için saklanıyor) (ON DELETE SET NULL)
                    ekleme_zamani TEXT NOT NULL, -- Ürünün adisyona eklenme zamanı (YYYY-MM-DD HH:MM:SS)
                    FOREIGN KEY (siparis_id) REFERENCES siparis_gecmisi(siparis_id) ON DELETE CASCADE, -- Sipariş silinirse detayları da sil
                    FOREIGN KEY (urun_id) REFERENCES urunler(urun_id) ON DELETE SET NULL,
                    FOREIGN KEY (kategori_id) REFERENCES kategoriler(kategori_id) ON DELETE SET NULL
                );
            """)

            # Müşteriler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS musteriler (
                    musteri_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_soyad TEXT NOT NULL,
                    telefon TEXT UNIQUE,
                    bakiye REAL DEFAULT 0.0
                );
            """)

             # Ödemeler tablosu (Parçalı ödemeleri veya tüm ödemeleri detaylandırmak için)
             # siparis_gecmisi'ndeki odenen_tutar alanını detaylandırmak için kullanılabilir
             # Şu anki implementasyonda siparis_gecmisi.odenen_tutar kullanılıyor,
             # bu tablo daha detaylı raporlama veya farklı ödeme türlerini saklamak için eklenebilir.
             # Şimdilik mevcut schema yeterli, bu tablo pasif kalsın veya ileriye dönük düşünülsün.
             # self.cursor.execute("""
             #     CREATE TABLE IF NOT EXISTS odemeler (
             #         odeme_id INTEGER PRIMARY KEY AUTOINCREMENT,
             #         siparis_id INTEGER NOT NULL,
             #         odeme_zamani TEXT NOT NULL,
             #         miktar REAL NOT NULL,
             #         odeme_yontemi TEXT, -- 'Nakit', 'Kart', 'Müşteri Bakiyesi'
             #         FOREIGN KEY (siparis_id) REFERENCES siparis_gecmisi(siparis_id) ON DELETE CASCADE
             #     );
             # """)

            # Ayarlar tablosu (Örn: Son arşivlenen yıl bilgisi)
            self.cursor.execute("""
                 CREATE TABLE IF NOT EXISTS settings (
                     key TEXT PRIMARY KEY,
                     value TEXT
                 );
             """)


            self.conn.commit()
            print("Veritabanı tabloları kontrol edildi/oluşturuldu.")
        except sqlite3.Error as e:
            print(f"Veritabanı tablo oluşturma hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Veritabanı tabloları oluşturulurken hata oluştu: {e}")
            if self.conn:
                self.conn.rollback()


    def _add_default_data(self):
        """Veritabanı boşsa varsayılan masa ve ürünleri ekler."""
        try:
            # Varsayılan masalar (sadece eğer hiç masa yoksa)
            self.cursor.execute("SELECT COUNT(*) FROM masalar")
            if self.cursor.fetchone()[0] == 0:
                for i in range(1, 11): # 10 tane varsayılan masa
                    self.cursor.execute("INSERT INTO masalar (masa_no) VALUES (?)", (i,))
                self.conn.commit()
                print("Varsayılan masalar eklendi.")

            # Varsayılan kategoriler (sadece eğer hiç kategori yoksa)
            self.cursor.execute("SELECT COUNT(*) FROM kategoriler")
            if self.cursor.fetchone()[0] == 0:
                # constants.py'deki DEFAULT_CATEGORIES listesini kullan
                kategoriler = [(cat,) for cat in constants.DEFAULT_CATEGORIES] # Tuple listesi oluştur
                self.cursor.executemany("INSERT INTO kategoriler (adi) VALUES (?)", kategoriler)
                self.conn.commit()
                print("Varsayılan kategoriler eklendi.")

            # Varsayılan ürünler (sadece eğer hiç ürün yoksa)
            self.cursor.execute("SELECT COUNT(*) FROM urunler")
            if self.cursor.fetchone()[0] == 0:
                # Kategori ID'lerini al
                self.cursor.execute("SELECT kategori_id, adi FROM kategoriler")
                kategori_map = {row['adi']: row['kategori_id'] for row in self.cursor.fetchall()}

                # constants.py'deki DEFAULT_PRODUCTS listesini kullan
                urunler_to_insert = []
                for urun_info in constants.DEFAULT_PRODUCTS:
                    adi, fiyat, kategori_adi, aktif_durumu, hizli_satis_sirasi = urun_info
                    kategori_id = kategori_map.get(kategori_adi) # Kategori adına göre ID'yi bul
                    urunler_to_insert.append((adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi))

                self.cursor.executemany("INSERT INTO urunler (adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi) VALUES (?, ?, ?, ?, ?)", urunler_to_insert)
                self.conn.commit()
                print("Varsayılan ürünler eklendi.")

        except sqlite3.Error as e:
            print(f"Veritabanı varsayılan veri ekleme hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Varsayılan veriler eklenirken hata oluştu: {e}")
            if self.conn:
                self.conn.rollback()

    # --- Ayarlar Metotları ---
    def get_setting(self, key, default_value=None):
         """Ayarlar tablosundan bir değeri okur."""
         try:
             self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
             result = self.cursor.fetchone()
             if result:
                  return result['value']
             return default_value
         except sqlite3.Error as e:
             print(f"Ayarlar okuma hatası (Anahtar: {key}): {e}")
             return default_value # Hata durumunda varsayılan değeri döndür

    def set_setting(self, key, value):
         """Ayarlar tablosuna bir değer yazar veya günceller."""
         try:
             self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
             self.conn.commit()
             return True
         except sqlite3.Error as e:
             print(f"Ayarlar yazma hatası (Anahtar: {key}, Değer: {value}): {e}")
             self.conn.rollback()
             return False


    # --- Arşivleme ve Temizleme Metotları ---
    def archive_and_delete_old_orders(self, year_to_process):
        """Belirtilen yıldan önceki tamamlanmış siparişleri arşivler ve ana DB'den siler."""
        print(f"Arşivleme ve silme işlemi başlatılıyor: {year_to_process} yılı ve öncesi...")

        try:
            # Arşivlenecek yılın son gününü belirle
            end_of_year = datetime(year_to_process, 12, 31, 23, 59, 59).strftime("%Y-%m-%d %H:%M:%S")

            # Arşivlenecek siparişleri ve detaylarını çek
            self.cursor.execute("""
                SELECT sg.siparis_id, sg.masa_no, sg.acilis_zamani, sg.kapanis_zamani,
                       sg.durum, sg.toplam_tutar, sg.iskonto, sg.odenen_tutar,
                       sg.odeme_yontemi, sg.son_islem_zamani, sg.musteri_id
                FROM siparis_gecmisi sg
                WHERE sg.durum = 'Kapandı' -- Sadece kapanmış adisyonlar
                  AND sg.kapanis_zamani <= ? -- Belirtilen yılın sonuna kadar olanlar
            """, (end_of_year,))
            orders_to_archive = self.cursor.fetchall()

            if not orders_to_archive:
                 print(f"{year_to_process} yılı ve öncesine ait arşivlenecek tamamlanmış sipariş bulunamadı.")
                 return True, f"{year_to_process} yılı ve öncesine ait arşivlenecek veri yok."

            print(f"Arşivlenecek toplam {len(orders_to_archive)} sipariş bulundu.")

            # Arşiv veritabanı dosya adını belirle
            archive_db_name = f'cafe_adisyon_archive_{year_to_process}.db'
            # Arşiv veritabanı bağlantısını kur
            archive_conn = None
            archive_cursor = None
            try:
                archive_conn = sqlite3.connect(archive_db_name)
                archive_cursor = archive_conn.cursor()
                archive_conn.row_factory = sqlite3.Row # Arşiv DB için de row_factory ayarla

                # Arşiv DB'de gerekli tabloları oluştur (ana DB'deki yapıyla aynı olmalı)
                archive_cursor.execute("""
                     CREATE TABLE IF NOT EXISTS siparis_gecmisi (
                         siparis_id INTEGER PRIMARY KEY, -- ID'yi koru
                         masa_no INTEGER,
                         acilis_zamani TEXT,
                         kapanis_zamani TEXT,
                         durum TEXT,
                         toplam_tutar REAL,
                         iskonto REAL,
                         odenen_tutar REAL,
                         odeme_yontemi TEXT,
                         son_islem_zamani TEXT,
                         musteri_id INTEGER -- Müşteri ID'sini koru
                     );
                 """)
                archive_cursor.execute("""
                     CREATE TABLE IF NOT EXISTS siparis_detaylari (
                         detay_id INTEGER PRIMARY KEY, -- ID'yi koru
                         siparis_id INTEGER NOT NULL,
                         urun_id INTEGER,
                         urun_adi TEXT NOT NULL,
                         miktar REAL NOT NULL,
                         birim_fiyat REAL NOT NULL,
                         tutar REAL NOT NULL,
                         kategori_id INTEGER,
                         ekleme_zamani TEXT NOT NULL -- Ekleme zamanı sütununu ekle
                     );
                 """)
                archive_conn.commit()

                # Sipariş detaylarını da çek ve arşiv DB'ye kopyala
                deleted_order_ids = [order['siparis_id'] for order in orders_to_archive]
                if deleted_order_ids:
                     # Sipariş detaylarını çek
                     placeholders = ','.join('?' for _ in deleted_order_ids)
                     self.cursor.execute(f"""
                         SELECT detay_id, siparis_id, urun_id, urun_adi, miktar, birim_fiyat, tutar, kategori_id, ekleme_zamani
                         FROM siparis_detaylari
                         WHERE siparis_id IN ({placeholders})
                     """, deleted_order_ids)
                     details_to_archive = self.cursor.fetchall()

                     # Detayları arşiv DB'ye kopyala
                     archive_cursor.executemany("""
                         INSERT OR IGNORE INTO siparis_detaylari (detay_id, siparis_id, urun_id, urun_adi, miktar, birim_fiyat, tutar, kategori_id, ekleme_zamani)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                     """, [(d['detay_id'], d['siparis_id'], d['urun_id'], d['urun_adi'], d['miktar'], d['birim_fiyat'], d['tutar'], d['kategori_id'], d['ekleme_zamani']) for d in details_to_archive])
                     archive_conn.commit()
                     print(f"Arşiv DB'ye {len(details_to_archive)} sipariş detayı kopyalandı.")


                # Siparişleri arşiv DB'ye kopyala
                archive_cursor.executemany("""
                    INSERT OR IGNORE INTO siparis_gecmisi (siparis_id, masa_no, acilis_zamani, kapanis_zamani, durum, toplam_tutar, iskonto, odenen_tutar, odeme_yontemi, son_islem_zamani, musteri_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [(o['siparis_id'], o['masa_no'], o['acilis_zamani'], o['kapanis_zamani'], o['durum'], o['toplam_tutar'], o['iskonto'], o['odenen_tutar'], o['odeme_yöntemi'], o['son_islem_zamani'], o['musteri_id']) for o in orders_to_archive])
                archive_conn.commit()
                print(f"Arşiv DB'ye {len(orders_to_archive)} sipariş kopyalandı.")


                print("Arşivleme başarılı.")

                # Ana DB'den silme işlemine geç
                # sipariş_detaylari'dan silme (FOREIGN KEY ON DELETE CASCADE olduğu için siparişler silinince detayları da silinecek)
                # Sadece siparis_gecmisi'nden silmek yeterli olabilir.
                self.cursor.execute(f"""
                    DELETE FROM siparis_gecmisi
                    WHERE siparis_id IN ({placeholders})
                """, deleted_order_ids)
                self.conn.commit()
                print(f"Ana DB'den {len(deleted_order_ids)} sipariş silindi.")

                # Ayarlar tablosunu güncelle (son arşivlenen yılı kaydet)
                self.set_setting("last_archived_year", year_to_process)

                return True, f"{year_to_process} yılı ve öncesine ait tamamlanmış siparişler başarıyla arşivlendi ve ana veritabanından silindi."

            except sqlite3.Error as e:
                print(f"Arşivleme veya silme hatası: {e}")
                messagebox.showerror("Veritabanı Hatası", f"Arşivleme veya silme işlemi sırasında hata oluştu: {e}")
                if archive_conn:
                     archive_conn.rollback()
                if self.conn:
                     self.conn.rollback()
                return False, f"Arşivleme veya silme işlemi sırasında hata oluştu: {e}"

            finally:
                # Arşiv DB bağlantısını kapat
                if archive_conn:
                    archive_conn.close()

        except Exception as e:
            print(f"Genel arşivleme/silme hatası: {e}")
            messagebox.showerror("Hata", f"Arşivleme/silme işlemi sırasında beklenmedik bir hata oluştu: {e}")
            return False, f"Arşivleme/silme işlemi sırasında beklenmedik bir hata oluştu: {e}"


    # --- Masa Metotları ---
    def get_all_masalar(self):
        """Tüm masaları veritabanından çeker (ilişkili müşteri adıyla birlikte)."""
        try:
            # Siparişi ve müşteriyi JOIN et, müşteri adı NULL olabilir (LEFT JOIN)
            self.cursor.execute("""
                SELECT
                    m.masa_no, m.durum, m.guncel_toplam, mu.ad_soyad AS musteri_adi
                FROM masalar m
                LEFT JOIN siparis_gecmisi sg ON m.aktif_siparis_id = sg.siparis_id
                LEFT JOIN musteriler mu ON sg.musteri_id = mu.musteri_id
                ORDER BY m.masa_no
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Masaları çekme hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Masalar yüklenirken hata oluştu: {e}")
            return []

    def get_masa_info(self, masa_no):
        """Belirli bir masanın bilgilerini çeker."""
        try:
            self.cursor.execute("SELECT masa_id, masa_no, durum, aktif_siparis_id, guncel_toplam, iskonto FROM masalar WHERE masa_no = ?", (masa_no,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Masa bilgisi çekme hatası (Masa {masa_no}): {e}")
            return None

    def update_masa_status(self, masa_no, status):
        """Belirli bir masanın durumunu günceller."""
        try:
            self.cursor.execute("UPDATE masalar SET durum = ? WHERE masa_no = ?", (status, masa_no))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Masa durumu güncelleme hatası (Masa {masa_no}, Durum {status}): {e}")
            self.conn.rollback()
            return False

    def update_masa_totals(self, masa_no, brut_total, discount_amount, odenen_tutar):
        """Belirli bir masanın toplam ve iskonto bilgilerini günceller."""
        try:
            net_total = brut_total - discount_amount
            # Masalar tablosunda guncel_toplam (net tutarı tutacak), iskonto güncelleniyor.
            self.cursor.execute("UPDATE masalar SET guncel_toplam = ?, iskonto = ? WHERE masa_no = ?",
                                (net_total, discount_amount, masa_no))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Masa toplamları güncelleme hatası (Masa {masa_no}): {e}")
            self.conn.rollback()
            return False


    def add_masa(self):
        """Yeni bir masa ekler."""
        try:
            self.cursor.execute("SELECT MAX(masa_no) FROM masalar")
            last_masa_no = self.cursor.fetchone()[0]
            next_masa_no = (last_masa_no or 0) + 1
            self.cursor.execute("INSERT INTO masalar (masa_no) VALUES (?)", (next_masa_no,))
            self.conn.commit()
            return next_masa_no
        except sqlite3.Error as e:
            print(f"Yeni masa ekleme hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Yeni masa eklenirken hata oluştu: {e}")
            self.conn.rollback()
            return None

    def delete_masa(self, masa_no):
        """Belirli bir masayı siler."""
        try:
            # Masa durumunu kontrol et (sadece boş masalar silinebilir, bu kontrol UI'da da yapılmalı)
            self.cursor.execute("SELECT durum FROM masalar WHERE masa_no = ?", (masa_no,))
            masa_info = self.cursor.fetchone()
            if masa_info and masa_info['durum'] != 'Boş':
                 return False, "Sadece boş masalar silinebilir."

            self.cursor.execute("DELETE FROM masalar WHERE masa_no = ?", (masa_no,))
            self.conn.commit()
            return True, f"Masa {masa_no} başarıyla silindi."
        except sqlite3.Error as e:
            print(f"Masa silme hatası (Masa {masa_no}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Masa {masa_no} silinirken hata oluştu: {e}")
            self.conn.rollback()
            return False, f"Masa {masa_no} silinirken hata oluştu: {e}"

    # --- Kategori Metotları ---
    def get_all_categories(self):
        """Tüm kategorileri veritabanından çeker."""
        try:
            self.cursor.execute("SELECT kategori_id, adi FROM kategoriler ORDER BY adi")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Kategori çekme hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Kategori listesi alınırken hata oluştu: {e}")
            return []

    def add_category(self, category_name):
        """Yeni bir kategori ekler."""
        try:
            self.cursor.execute("INSERT INTO kategoriler (adi) VALUES (?)", (category_name,))
            self.conn.commit()
            return True, "Kategori başarıyla eklendi."
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, f"'{category_name}' adında bir kategori zaten mevcut."
        except sqlite3.Error as e:
            print(f"Kategori ekleme hatası ('{category_name}'): {e}")
            self.conn.rollback()
            return False, f"Kategori eklenirken hata oluştu: {e}"

    def delete_category(self, category_name):
        """Belirli bir kategoriyi siler."""
        try:
            # Kategoriye bağlı ürün var mı kontrol et (silme işlemi engelleniyor)
            self.cursor.execute("SELECT kategori_id FROM kategoriler WHERE adi = ?", (category_name,))
            category_info = self.cursor.fetchone()
            if not category_info:
                 return False, f"'{category_name}' adında bir kategori bulunamadı."

            kategori_id = category_info['kategori_id']

            self.cursor.execute("SELECT COUNT(*) FROM urunler WHERE kategori_id = ?", (kategori_id,))
            product_count = self.cursor.fetchone()[0]

            if product_count > 0:
                 # FK ON DELETE SET NULL olsa da, silme işlemini burada engelleyelim ve kullanıcıya bildirelim.
                 return False, f"Bu kategoriye bağlı {product_count} ürün olduğu için silinemez. Lütfen önce ürünleri pasifleştirin veya kategorilerini değiştirin."


            self.cursor.execute("DELETE FROM kategoriler WHERE kategori_id = ?", (kategori_id,))
            self.conn.commit()
            return True, f"'{category_name}' kategorisi başarıyla silindi."
        except sqlite3.Error as e:
            print(f"Kategori silme hatası ('{category_name}'): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Kategori silinirken hata oluştu: {e}")
            self.conn.rollback()
            return False, f"Kategori silinirken hata oluştu: {e}"


    # --- Ürün Metotları ---
    def get_all_products(self, include_inactive=False):
        """Tüm ürünleri (veya sadece aktif olanları) çeker."""
        try:
            query = """
                SELECT
                    u.urun_id, u.adi, u.fiyat, k.adi AS kategori_adi, u.aktif_durumu, u.hizli_satis_sirasi, u.kategori_id
                FROM urunler u
                LEFT JOIN kategoriler k ON u.kategori_id = k.kategori_id
            """
            if not include_inactive:
                query += " WHERE u.aktif_durumu = 1"

            query += " ORDER BY u.hizli_satis_sirasi, u.adi" # Önce hızlı satış sırası, sonra alfabetik

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ürünleri çekme hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Ürünler yüklenirken hata oluştu: {e}")
            return []

    def get_product_by_id(self, urun_id):
         """Belirli bir ürünü ID'sine göre çeker."""
         try:
             self.cursor.execute("""
                 SELECT
                     u.urun_id, u.adi, u.fiyat, k.adi AS kategori_adi, u.aktif_durumu, u.hizli_satis_sirasi, u.kategori_id
                 FROM urunler u
                 LEFT JOIN kategoriler k ON u.kategori_id = k.kategori_id
                 WHERE u.urun_id = ?
             """, (urun_id,))
             return self.cursor.fetchone()
         except sqlite3.Error as e:
             print(f"Ürün çekme hatası (ID {urun_id}): {e}")
             return None


    def add_product(self, adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi):
        """Yeni bir ürün ekler."""
        try:
            self.cursor.execute("""
                INSERT INTO urunler (adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi)
                VALUES (?, ?, ?, ?, ?)
            """, (adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi))
            self.conn.commit()
            return True, f"'{adi}' ürünü başarıyla eklendi."
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, f"'{adi}' adında bir ürün zaten mevcut."
        except sqlite3.Error as e:
            print(f"Ürün ekleme hatası ('{adi}'): {e}")
            self.conn.rollback()
            return False, f"Ürün eklenirken hata oluştu: {e}"

    def update_product(self, urun_id, adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi):
        """Mevcut bir ürünü günceller."""
        try:
            self.cursor.execute("""
                UPDATE urunler
                SET adi = ?, fiyat = ?, kategori_id = ?, aktif_durumu = ?, hizli_satis_sirasi = ?
                WHERE urun_id = ?
            """, (adi, fiyat, kategori_id, aktif_durumu, hizli_satis_sirasi, urun_id))
            self.conn.commit()
            return True, f"'{adi}' ürünü başarıyla güncellendi."
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, f"'{adi}' adında başka bir ürün zaten mevcut."
        except sqlite3.Error as e:
            print(f"Ürün güncelleme hatası (ID {urun_id}, '{adi}'): {e}")
            self.conn.rollback()
            return False, f"Ürün güncellenirken hata oluştu: {e}"

    def mark_product_inactive(self, urun_id):
        """Bir ürünü aktif_durumu = 0 yaparak pasif hale getirir."""
        try:
            self.cursor.execute("UPDATE urunler SET aktif_durumu = 0 WHERE urun_id = ?", (urun_id,))
            self.conn.commit()
            return True, "Ürün başarıyla pasif hale getirildi."
        except sqlite3.Error as e:
            print(f"Ürün pasifleştirme hatası (ID {urun_id}): {e}")
            self.conn.rollback()
            return False, f"Ürün pasif hale getirilirken hata oluştu: {e}"

    def mark_product_active(self, urun_id):
         """Bir ürünü aktif_durumu = 1 yaparak aktif hale getirir."""
         try:
             self.cursor.execute("UPDATE urunler SET aktif_durumu = 1 WHERE urun_id = ?", (urun_id,))
             self.conn.commit()
             return True, "Ürün başarıyla aktif hale getirildi."
         except sqlite3.Error as e:
             print(f"Ürün aktif hale getirme hatası (ID {urun_id}): {e}")
             self.conn.rollback()
             return False, f"Ürün aktif hale getirilirken hata oluştu: {e}"


    # --- Sipariş ve Adisyon Metotları ---
    def get_order_details(self, siparis_id):
        """Belirli bir siparişin detaylarını (ürünlerini) çeker."""
        try:
            # ekleme_zamani sütunu eklendi
            self.cursor.execute("""
                SELECT detay_id, urun_id, urun_adi, miktar, birim_fiyat, tutar, kategori_id, ekleme_zamani
                FROM siparis_detaylari
                WHERE siparis_id = ?
            """, (siparis_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Sipariş detayları çekme hatası (Sipariş ID {siparis_id}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Sipariş detayları yüklenirken hata oluştu: {e}")
            return []

    def get_order_info(self, siparis_id):
         """Belirli bir siparişin temel bilgilerini çeker."""
         try:
             self.cursor.execute("""
                 SELECT siparis_id, masa_no, acilis_zamani, kapanis_zamani, durum,
                        toplam_tutar, iskonto, odenen_tutar, odeme_yontemi,
                        son_islem_zamani, musteri_id
                 FROM siparis_gecmisi
                 WHERE siparis_id = ?
             """, (siparis_id,))
             return self.cursor.fetchone()
         except sqlite3.Error as e:
             print(f"Sipariş bilgisi çekme hatası (Sipariş ID {siparis_id}): {e}")
             return None

    def create_new_order(self, masa_no):
        """Yeni bir sipariş (adisyon) oluşturur."""
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO siparis_gecmisi (masa_no, acilis_zamani, durum, son_islem_zamani, toplam_tutar, iskonto, odenen_tutar)
                VALUES (?, ?, ?, ?, 0.0, 0.0, 0.0)
            """, (masa_no, now, 'Açık', now))
            siparis_id = self.cursor.lastrowid
            # Masa durumunu ve aktif sipariş ID'sini güncelle
            self.cursor.execute("UPDATE masalar SET aktif_siparis_id = ?, durum = 'Dolu', guncel_toplam = 0.0, iskonto = 0.0 WHERE masa_no = ?",
                                (siparis_id, masa_no))
            self.conn.commit()
            print(f"Yeni sipariş oluşturuldu. ID: {siparis_id} (Masa {masa_no})")
            return siparis_id
        except sqlite3.Error as e:
            print(f"Yeni sipariş oluşturma hatası (Masa {masa_no}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Yeni sipariş oluşturulurken hata oluştu: {e}")
            self.conn.rollback()
            return None

    # add_order_item metodu, ürün ekleme ve miktarı güncelleme için kullanılacak.
    # Eğer detay_id None ise yeni kayıt ekler ve ekleme_zamani'nı kaydeder.
    # Varsa mevcut kaydı günceller (ekleme_zamani değişmez).
    def add_order_item(self, siparis_id, urun_id, urun_adi, miktar, birim_fiyat, kategori_id, detay_id=None):
        """Bir siparişe ürün ekler veya mevcut ürünün miktarını günceller."""
        try:
            tutar = miktar * birim_fiyat
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if detay_id is None:
                # Yeni ürün ekle
                self.cursor.execute("""
                    INSERT INTO siparis_detaylari (siparis_id, urun_id, urun_adi, miktar, birim_fiyat, tutar, kategori_id, ekleme_zamani)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (siparis_id, urun_id, urun_adi, miktar, birim_fiyat, tutar, kategori_id, now))
                new_detay_id = self.cursor.lastrowid
                # print(f"Yeni sipariş detayı eklendi. Detay ID: {new_detay_id}, Ürün: {urun_adi} x {miktar}") # Debug
            else:
                # Mevcut ürünün miktarını güncelle (ekleme_zamani değişmez)
                self.cursor.execute("""
                    UPDATE siparis_detaylari
                    SET miktar = ?, tutar = ?
                    WHERE detay_id = ? AND siparis_id = ?
                """, (miktar, tutar, detay_id, siparis_id))
                new_detay_id = detay_id # Güncelleme işleminde ID değişmez
                # print(f"Sipariş detayı güncellendi. Detay ID: {detay_id}, Ürün: {urun_adi} x {miktar}") # Debug


            # Siparişin brüt toplamını ve son işlem zamanını güncelle
            self.cursor.execute("""
                UPDATE siparis_gecmisi
                SET toplam_tutar = (SELECT COALESCE(SUM(tutar), 0.0) FROM siparis_detaylari WHERE siparis_id = ?),
                    son_islem_zamani = ?
                WHERE siparis_id = ?
            """, (siparis_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), siparis_id))

            # Masa durumunu ve son işlem zamanını güncelle
            self.cursor.execute("""
                UPDATE masalar
                SET durum = 'Dolu' -- Ürün eklendiğinde/güncellendiğinde masa dolu olur
                WHERE aktif_siparis_id = ?
            """, (siparis_id,))

            self.conn.commit()
            return True, new_detay_id # Başarı ve işlem yapılan detay_id'yi döndür
        except sqlite3.Error as e:
            print(f"Sipariş detay ekleme/güncelleme hatası (Sipariş ID {siparis_id}, Ürün '{urun_adi}'): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Ürün sepete eklenirken/güncellenirken hata oluştu: {e}")
            self.conn.rollback()
            return False, None


    def remove_order_item(self, detay_id, siparis_id):
        """Bir siparişten belirli bir detay öğesini siler."""
        try:
            # Silinecek detayın ait olduğu siparişin ID'sinin doğruluğunu kontrol etmek iyi olabilir.
            # self.cursor.execute("SELECT siparis_id FROM siparis_detaylari WHERE detay_id = ?", (detay_id,))
            # result = self.cursor.fetchone()
            # if not result or result['siparis_id'] != siparis_id:
            #      return False, "Silinecek ürün detayı bulunamadı veya yanlış siparişe ait."


            self.cursor.execute("DELETE FROM siparis_detaylari WHERE detay_id = ?", (detay_id,))

            # Siparişin brüt toplamını ve son işlem zamanını güncelle
            self.cursor.execute("""
                UPDATE siparis_gecmisi
                SET toplam_tutar = (SELECT COALESCE(SUM(tutar), 0.0) FROM siparis_detaylari WHERE siparis_id = ?),
                    son_islem_zamani = ?
                WHERE siparis_id = ?
            """, (siparis_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), siparis_id))

            # Masa durumunu ve son işlem zamanını güncelle (eğer tüm ürünler silindiyse durum 'Boş' olabilir, AdisyonTab bunu yönetecek)
            # Masa tablosindeki guncel_toplam ve iskonto AdisyonTab'da load_cart çağrılınca güncelleniyor.
            self.cursor.execute("""
                 UPDATE masalar
                 SET aktif_siparis_id = ? -- Tekrar atama veya emin olma
                 WHERE aktif_siparis_id = ?
            """, (siparis_id, siparis_id))


            self.conn.commit()
            return True, None
        except sqlite3.Error as e:
            print(f"Sipariş detay silme hatası (Detay ID {detay_id}, Sipariş ID {siparis_id}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Ürün sepetten silinirken hata oluştu: {e}")
            self.conn.rollback()
            return False, None

    def clear_order_details(self, siparis_id):
        """Bel belirli bir siparişin tüm detaylarını siler (sepeti temizler) ve siparişi iptal eder."""
        try:
            # Detayları sil
            self.cursor.execute("DELETE FROM siparis_detaylari WHERE siparis_id = ?", (siparis_id,))

            # Siparişi 'İptal Edildi' olarak işaretle ve toplamları sıfırla
            self.cursor.execute("""
                UPDATE siparis_gecmisi
                SET toplam_tutar = 0.0, iskonto = 0.0, odenen_tutar = 0.0,
                    durum = 'İptal Edildi', kapanis_zamani = ?, son_islem_zamani = NULL,
                    musteri_id = NULL -- Müşteri ilişkisini de kopar
                WHERE siparis_id = ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), siparis_id))

            # Masanın durumunu ve ilişkili sipariş bilgisini sıfırla
            self.cursor.execute("""
                UPDATE masalar
                SET aktif_siparis_id = NULL, durum = 'Boş', guncel_toplam = 0.0, iskonto = 0.0
                WHERE aktif_siparis_id = ?
            """, (siparis_id,))

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Sipariş detayları temizleme hatası (Sipariş ID {siparis_id}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Sepet temizlenirken hata oluştu: {e}")
            self.conn.rollback()
            return False

    def update_order_discount(self, siparis_id, discount_amount):
        """Belirli bir siparişe iskonto uygular ve sipariş/masa toplamlarını günceller."""
        try:
            self.cursor.execute("""
                UPDATE siparis_gecmisi
                SET iskonto = ?, son_islem_zamani = ?
                WHERE siparis_id = ?
            """, (discount_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), siparis_id))

            # Masa üzerindeki iskonto alanını da güncelle
            self.cursor.execute("""
                 UPDATE masalar
                 SET iskonto = ?
                 WHERE aktif_siparis_id = ?
            """, (discount_amount, siparis_id))

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Sipariş iskonto güncelleme hatası (Sipariş ID {siparis_id}, İskonto {discount_amount}): {e}")
            self.conn.rollback()
            return False

    def record_partial_payment(self, siparis_id, amount, payment_method="Ara Ödeme"):
         """Sipariş için parçalı ödeme kaydeder."""
         try:
             # siparis_gecmisi tablosundaki odenen_tutar alanını güncelle
             self.cursor.execute("""
                 UPDATE siparis_gecmisi
                 SET odenen_tutar = odenen_tutar + ?,
                     son_islem_zamani = ?
                 WHERE siparis_id = ?
             """, (amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), siparis_id))

             # Masa üzerindeki son işlem zamanını güncelle
             self.cursor.execute("""
                  UPDATE masalar
                  SET aktif_siparis_id = ? -- Tekrar atama veya emin olma
                  WHERE aktif_siparis_id = ?
             """, (siparis_id, siparis_id))


             self.conn.commit()
             return True
         except sqlite3.Error as e:
             print(f"Parçalı ödeme kaydetme hatası (Sipariş ID {siparis_id}, Miktar {amount}): {e}")
             self.conn.rollback()
             return False


    def process_full_payment(self, siparis_id, payment_method):
        """Siparişin kalan tutarını kapatır ve adisyonu sonlandırır."""
        try:
            # Güncel sipariş bilgisini al
            order_info = self.get_order_info(siparis_id)
            if not order_info:
                 return False, "Sipariş bulunamadı."

            brut_toplam = order_info['toplam_tutar'] or 0.0
            iskonto = order_info['iskonto'] or 0.0
            odenen_tutar_current = order_info['odenen_tutar'] or 0.0
            net_toplam = brut_toplam - iskonto
            kalan_tutar = net_toplam - odenen_tutar_current

            # Kalan tutar negatifse veya 0'dan küçükse (fazla ödeme veya hata)
            # Normal ödeme akışında kalan tutarı 0'a tamamlarız.
            if kalan_tutar > 0:
                 odenen_tutar_current += kalan_tutar # Kalanı ödenen tutara ekle
            # else: kalan tutar <= 0 ise zaten ya tam ödenmiştir ya da fazla ödenmiştir,
            # odenen_tutar_current olduğu gibi kalır.

            # Siparişi 'Kapandı' olarak işaretle, kapanış zamanı, nihai toplamlar ve ödeme yöntemini kaydet
            self.cursor.execute("""
                UPDATE siparis_gecmisi
                SET kapanis_zamani = ?, durum = 'Kapandı',
                    toplam_tutar = ?, iskonto = ?, odenen_tutar = ?, -- Kapanış anındaki nihai değerler
                    odeme_yontemi = ?, son_islem_zamani = NULL -- Kapalı siparişlerde son işlem zamanı olmaz
                WHERE siparis_id = ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), brut_toplam, iskonto, odenen_tutar_current, payment_method, siparis_id))

            # Masanın durumunu ve ilişkili sipariş bilgisini sıfırla
            self.cursor.execute("""
                UPDATE masalar
                SET aktif_siparis_id = NULL, durum = 'Boş', guncel_toplam = 0.0, iskonto = 0.0
                WHERE aktif_siparis_id = ?
            """, (siparis_id,))

            self.conn.commit()
            return True, net_toplam # Net toplamı döndür (raporlama için kullanılabilir)
        except sqlite3.Error as e:
            print(f"Tam ödeme işleme hatası (Sipariş ID {siparis_id}, Yöntem {payment_method}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Ödeme işlemi sırasında hata oluştu: {e}")
            self.conn.rollback()
            return False, 0.0

    def link_customer_to_order(self, siparis_id, musteri_id):
         """Bel belirli bir siparişi belirli bir müşteri ile ilişkilendirir."""
         try:
             self.cursor.execute("""
                 UPDATE siparis_gecmisi
                 SET musteri_id = ?, son_islem_zamani = ?
                 WHERE siparis_id = ?
             """, (musteri_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), siparis_id))
             self.conn.commit()
             return True
         except sqlite3.Error as e:
             print(f"Müşteri siparişe bağlama hatası (Sipariş ID {siparis_id}, Müşteri ID {musteri_id}): {e}")
             self.conn.rollback()
             return False

    def get_late_table_info(self):
        """Geçikmiş olabilecek dolu masaların bilgilerini çeker."""
        # DatabaseManager artık sadece bilgiyi çekiyor, geçikmiş kontrolü MasaTab'da
        try:
            self.cursor.execute(f"""
                SELECT m.masa_no, m.durum, sg.son_islem_zamani, m.aktif_siparis_id
                FROM masalar m
                JOIN siparis_gecmisi sg ON m.aktif_siparis_id = sg.siparis_id
                WHERE m.durum IN ('Dolu', 'Geçikmiş')
                  AND sg.son_islem_zamani IS NOT NULL
            """)
            results = self.cursor.fetchall()
            return results

        except sqlite3.Error as e:
            print(f"Geçikmiş masa bilgi çekme hatası: {e}")
            return []


    # --- Müşteri Metotları ---
    # get_all_customers artık müşteri ID'sini de döndürüyor
    def get_all_customers(self):
        """Tüm müşterileri veritabanından çeker."""
        try:
            self.cursor.execute("SELECT musteri_id, ad_soyad, telefon, bakiye FROM musteriler ORDER BY ad_soyad")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Müşterileri çekme hatası: {e}")
            messagebox.showerror("Veritabanı Hatası", f"Müşteri listesi yüklenirken hata oluştu: {e}")
            return []

    def get_customer_by_id(self, musteri_id):
        """Belirli bir müşteriyi ID'sine göre çeker."""
        try:
            self.cursor.execute("SELECT musteri_id, ad_soyad, telefon, bakiye FROM musteriler WHERE musteri_id = ?", (musteri_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Müşteri çekme hatası (ID {musteri_id}): {e}")
            return None

    def get_customer_by_phone(self, telefon):
         """Belirli bir müşteriyi telefon numarasına göre çeker."""
         try:
             self.cursor.execute("SELECT musteri_id, ad_soyad, telefon, bakiye FROM musteriler WHERE telefon = ?", (telefon,))
             return self.cursor.fetchone()
         except sqlite3.Error as e:
             print(f"Müşteri çekme hatası (Telefon {telefon}): {e}")
             return None


    def add_customer(self, ad_soyad, telefon):
        """Yeni bir müşteri ekler."""
        try:
            self.cursor.execute("INSERT INTO musteriler (ad_soyad, telefon) VALUES (?, ?)", (ad_soyad, telefon if telefon else None))
            self.conn.commit()
            return True, "Müşteri başarıyla eklendi."
        except sqlite3.IntegrityError:
             self.conn.rollback()
             return False, f"'{telefon}' numaralı bir müşteri zaten mevcut."
        except sqlite3.Error as e:
            print(f"Müşteri ekleme hatası ('{ad_soyad}'): {e}")
            self.conn.rollback()
            return False, f"Müşteri eklenirken hata oluştu: {e}"

    def update_customer(self, musteri_id, ad_soyad, telefon):
        """Mevcut bir müşteriyi günceller."""
        try:
            self.cursor.execute("""
                UPDATE musteriler
                SET ad_soyad = ?, telefon = ?
                WHERE musteri_id = ?
            """, (ad_soyad, telefon if telefon else None, musteri_id))
            self.conn.commit()
            return True, "Müşteri başarıyla güncellendi."
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False, f"'{telefon}' numaralı başka bir müşteri zaten mevcut."
        except sqlite3.Error as e:
            print(f"Müşteri güncelleme hatası (ID {musteri_id}, '{ad_soyad}'): {e}")
            self.conn.rollback()
            return False, f"Müşteri güncellenirken hata oluştu: {e}"

    def delete_customer(self, musteri_id):
        """Belirli bir müşteriyi siler."""
        try:
            # Müşteriye bağlı sipariş var mı kontrol et (silme işlemi engelleniyor)
            self.cursor.execute("SELECT COUNT(*) FROM siparis_gecmisi WHERE musteri_id = ?", (musteri_id,))
            kullanim_sayisi = self.cursor.fetchone()[0]

            if kullanim_sayisi > 0:
                 return False, f"Bu müşteri geçmiş adisyonlarda kullanıldığı için silinemez."

            self.cursor.execute("DELETE FROM musteriler WHERE musteri_id = ?", (musteri_id,))
            self.conn.commit()
            return True, "Müşteri başarıyla silindi."
        except sqlite3.Error as e:
            print(f"Müşteri silme hatası (ID {musteri_id}): {e}")
            self.conn.rollback()
            return False, f"Müşteri silinirken hata oluştu: {e}"

    def update_customer_balance(self, musteri_id, amount):
         """Müşterinin bakiyesini günceller (pozitif miktar yükleme, negatif miktar tahsilat)."""
         try:
             self.cursor.execute("UPDATE musteriler SET bakiye = bakiye + ? WHERE musteri_id = ?", (amount, musteri_id))
             self.conn.commit()
             return True
         except sqlite3.Error as e:
             print(f"Müşteri bakiye güncelleme hatası (ID {musteri_id}, Miktar {amount}): {e}")
             self.conn.rollback()
             return False

    # --- Raporlama Metotları ---
    def get_sales_summary(self, start_date, end_date):
        """Bel belirli bir tarih aralığındaki satış özetini çeker."""
        try:
            # Tarih formatı:YYYY-MM-DD
            # siparis_gecmisi'ndeki kapanis_zamani kullanılır.
            self.cursor.execute("""
                SELECT
                    COUNT(siparis_id) as toplam_adisyon,
                    SUM(toplam_tutar) as brut_satis,
                    SUM(iskonto) as toplam_iskonto,
                    SUM(odenen_tutar) as net_satis -- Kapanış anındaki toplam odenen tutar net satışı verir
                FROM siparis_gecmisi
                WHERE durum = 'Kapandı'
                  AND date(kapanis_zamani) BETWEEN date(?) AND date(?)
            """, (start_date, end_date))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Satış özeti çekme hatası ({start_date} - {end_date}): {e}")
            messagebox.showerror("Veritabanı Hatası", f"Satış özeti alınırken hata oluştu: {e}")
            return None

    def get_product_sales_report(self, start_date, end_date):
         """Belirli bir tarih aralığındaki ürün satış detaylarını çeker."""
         try:
             self.cursor.execute("""
                 SELECT
                     sd.urun_adi,
                     SUM(sd.miktar) as toplam_miktar,
                     SUM(sd.tutar) as toplam_tutar_urun,
                     k.adi AS kategori_adi
                 FROM siparis_detaylari sd
                 JOIN siparis_gecmisi sg ON sd.siparis_id = sg.siparis_id
                 LEFT JOIN kategoriler k ON sd.kategori_id = k.kategori_id
                 WHERE sg.durum = 'Kapandı'
                   AND date(sg.kapanis_zamani) BETWEEN date(?) AND date(?)
                 GROUP BY sd.urun_adi, k.adi
                 ORDER BY toplam_tutar_urun DESC
             """, (start_date, end_date))
             return self.cursor.fetchall()
         except sqlite3.Error as e:
             print(f"Ürün satış raporu çekme hatası ({start_date} - {end_date}): {e}")
             messagebox.showerror("Veritabanı Hatası", f"Ürün satış raporu alınırken hata oluştu: {e}")
             return []

    # Diğer raporlama metotları buraya eklenebilir (kategori bazlı, müşteri bazlı vb.)