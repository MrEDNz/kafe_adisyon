import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from core.database import Database

class MasaModule:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.masa_buttons = {}
        self.secili_masa = None
        self.setup_styles()
        self.setup_ui()
        self.load_masalar()
    
    def setup_styles(self):
        """TTK buton stillerini tanımlar"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Dolu.TButton', background='#ffcccc', foreground='black', font=('Helvetica', 10), padding=5)
        style.configure('Rezerve.TButton', background='#ffffcc', foreground='black', font=('Helvetica', 10), padding=5)
        style.configure('Bos.TButton', background='#ccffcc', foreground='black', font=('Helvetica', 10), padding=5)
    
    def setup_ui(self):
        """Arayüz bileşenlerini oluşturur"""
        try:
            # Ana çerçeve
            self.main_frame = ttk.Frame(self.frame)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Kontrol paneli
            control_frame = ttk.Frame(self.main_frame)
            control_frame.pack(fill=tk.X, pady=5)
            
            # Butonlar
            ttk.Button(control_frame, text="Masa Ekle", command=self.masa_ekle_form).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Masa Düzenle", command=self.duzenle_secili_masa).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Masa Sil", command=self.sil_secili_masa).pack(side=tk.LEFT, padx=5)
            ttk.Button(control_frame, text="Masa Taşı", command=self.masa_tasi).pack(side=tk.LEFT, padx=5)
            
            # Scrollable alan
            self.setup_scrollable_area()
            
            # Bilgi paneli
            self.setup_info_panel()
            
        except Exception as e:
            messagebox.showerror("Arayüz Hatası", f"Arayüz oluşturulamadı: {str(e)}")
            raise

    def setup_scrollable_area(self):
        """Kaydırılabilir alanı oluşturur"""
        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(container)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"),
                width=e.width
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.grid_frame = ttk.Frame(self.scrollable_frame)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

    def setup_info_panel(self):
        """Bilgi panelini oluşturur"""
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Masa Bilgisi")
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.info_labels = {
            'numara': ttk.Label(self.info_frame, text="Masa No: -"),
            'isim': ttk.Label(self.info_frame, text="İsim: -"),
            'durum': ttk.Label(self.info_frame, text="Durum: -"),
            'bakiye': ttk.Label(self.info_frame, text="Bakiye: 0.00 ₺")
        }
        
        for label in self.info_labels.values():
            label.pack(side=tk.LEFT, padx=10)
            
        ttk.Button(self.info_frame, text="Sipariş Ekle", command=self.siparis_ekle).pack(side=tk.RIGHT, padx=5)

    def load_masalar(self):
        """Masaları veritabanından yükler ve arayüzde gösterir"""
        try:
            # Önceki butonları temizle
            for widget in self.grid_frame.winfo_children():
                widget.destroy()
            self.masa_buttons = {}
            
            # Veritabanından masaları çek
            masalar = self.db.execute(
                "SELECT * FROM masalar ORDER BY masa_no", 
                fetch=True
            )
            
            if not masalar:
                messagebox.showinfo("Bilgi", "Masa bulunamadı, lütfen yeni masa ekleyin.")
                return
                
            # Grid oluştur
            for i, masa in enumerate(masalar):
                row = i // 6
                col = i % 6
                
                btn_text = f"Masa {masa['masa_no']}"
                if masa.get('isim'):
                    btn_text = f"{masa['isim']}\n{btn_text}"
                
                btn = ttk.Button(
                    self.grid_frame,
                    text=btn_text,
                    command=lambda m=masa['masa_id']: self.masa_sec(m),
                    width=15,
                    style=f"{masa.get('durum', 'Bos')}.TButton"
                )
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.masa_buttons[masa['masa_id']] = btn
            
            # Grid ayarları
            for i in range(6):
                self.grid_frame.columnconfigure(i, weight=1)
            
            rows_needed = (len(masalar) // 6) + 1
            for i in range(rows_needed):
                self.grid_frame.rowconfigure(i, weight=1)
                
        except Exception as e:
            messagebox.showerror("Hata", f"Masalar yüklenemedi: {str(e)}")

    def masa_ekle_form(self):
        """Yeni masa ekleme formunu açar"""
        self.ekle_pencere = tk.Toplevel(self.root)
        self.ekle_pencere.title("Yeni Masa Ekle")
        self.ekle_pencere.resizable(False, False)
        
        ttk.Label(self.ekle_pencere, text="Masa No:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_masa_no = ttk.Entry(self.ekle_pencere)
        self.entry_masa_no.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.ekle_pencere, text="Masa Adı:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_masa_adi = ttk.Entry(self.ekle_pencere)
        self.entry_masa_adi.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.ekle_pencere, text="Kaydet", command=self.masa_ekle).grid(row=2, columnspan=2, pady=10)

    def masa_ekle(self):
        """Veritabanına yeni masa ekler"""
        try:
            masa_no = int(self.entry_masa_no.get())
            masa_adi = self.entry_masa_adi.get().strip() or None
            
            # Masa numarası kontrolü
            existing = self.db.execute(
                "SELECT 1 FROM masalar WHERE masa_no=?",
                (masa_no,),
                fetch=True
            )
            if existing:
                messagebox.showerror("Hata", "Bu masa numarası zaten kayıtlı!")
                return
            
            # Transaction başlat
            self.db.execute("BEGIN TRANSACTION")
            
            # Masa ekleme sorgusu
            self.db.execute(
                "INSERT INTO masalar (masa_no, isim, durum) VALUES (?, ?, 'Boş')",
                (masa_no, masa_adi)
            )
            
            # Transaction'ı onayla
            self.db.execute("COMMIT")
            
            messagebox.showinfo("Başarılı", "Masa başarıyla eklendi!")
            self.ekle_pencere.destroy()
            self.load_masalar()
            
        except ValueError:
            messagebox.showerror("Hata", "Masa no sayı olmalıdır!")
        except Exception as e:
            self.db.execute("ROLLBACK")
            messagebox.showerror("Hata", f"Masa eklenemedi: {str(e)}")

    def sil_secili_masa(self):
        """Seçili masayı siler"""
        if not self.secili_masa:
            messagebox.showwarning("Uyarı", "Önce bir masa seçmelisiniz!")
            return
            
        # Masa bilgilerini al
        masa = self.db.execute(
            "SELECT * FROM masalar WHERE masa_id=?",
            (self.secili_masa,),
            fetch=True
        )
        
        if not masa:
            messagebox.showerror("Hata", "Masa bulunamadı!")
            return
            
        masa = masa[0]
        
        # Onay sorusu
        if not messagebox.askyesno(
            "Onay", 
            f"{masa['masa_no']} numaralı masayı ve bağlı siparişleri silmek istediğinize emin misiniz?"
        ):
            return
        
        try:
            # Transaction başlat
            self.db.execute("BEGIN TRANSACTION")
            
            # Bağlı siparişleri sil
            self.db.execute(
                "DELETE FROM siparisler WHERE masa_id=?",
                (self.secili_masa,)
            )
            
            # Masayı sil
            self.db.execute(
                "DELETE FROM masalar WHERE masa_id=?",
                (self.secili_masa,)
            )
            
            # Transaction'ı onayla
            self.db.execute("COMMIT")
            
            messagebox.showinfo("Başarılı", "Masa ve bağlı siparişler silindi!")
            self.secili_masa = None
            self.load_masalar()
            
            # Bilgi panelini temizle
            for label in self.info_labels.values():
                label.config(text=label.cget("text").split(":")[0] + ": -")
            self.info_labels['bakiye'].config(text="Bakiye: 0.00 ₺")
            
        except Exception as e:
            self.db.execute("ROLLBACK")
            messagebox.showerror("Hata", f"Masa silinemedi: {str(e)}")

    def duzenle_secili_masa(self):
        """Seçili masayı düzenler"""
        if not self.secili_masa:
            messagebox.showwarning("Uyarı", "Önce bir masa seçmelisiniz!")
            return
            
        # Masa bilgilerini al
        masa = self.db.execute(
            "SELECT * FROM masalar WHERE masa_id=?",
            (self.secili_masa,),
            fetch=True
        )
        
        if not masa:
            messagebox.showerror("Hata", "Masa bulunamadı!")
            return
            
        masa = masa[0]
        
        # Düzenleme penceresi
        self.duzenle_pencere = tk.Toplevel(self.root)
        self.duzenle_pencere.title(f"Masa Düzenle - {masa['masa_no']}")
        self.duzenle_pencere.resizable(False, False)
        
        # Masa No
        ttk.Label(self.duzenle_pencere, text="Masa No:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.duzenle_pencere, text=str(masa['masa_no'])).grid(row=0, column=1, padx=5, pady=5)
        
        # Masa Adı
        ttk.Label(self.duzenle_pencere, text="Masa Adı:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_isim = ttk.Entry(self.duzenle_pencere)
        self.entry_isim.insert(0, masa['isim'] or "")
        self.entry_isim.grid(row=1, column=1, padx=5, pady=5)
        
        # Durum
        ttk.Label(self.duzenle_pencere, text="Durum:").grid(row=2, column=0, padx=5, pady=5)
        self.combo_durum = ttk.Combobox(
            self.duzenle_pencere, 
            values=["Boş", "Dolu", "Rezerve"], 
            state="readonly"
        )
        self.combo_durum.set(masa['durum'])
        self.combo_durum.grid(row=2, column=1, padx=5, pady=5)
        
        # Kaydet Butonu
        ttk.Button(
            self.duzenle_pencere, 
            text="Kaydet", 
            command=self.kaydet_duzenleme
        ).grid(row=3, columnspan=2, pady=10)

    def kaydet_duzenleme(self):
        """Düzenleme penceresindeki değişiklikleri kaydeder"""
        try:
            yeni_isim = self.entry_isim.get().strip() or None
            yeni_durum = self.combo_durum.get()
            
            self.db.execute(
                "UPDATE masalar SET isim=?, durum=? WHERE masa_id=?",
                (yeni_isim, yeni_durum, self.secili_masa)
            )
            
            messagebox.showinfo("Başarılı", "Masa bilgileri güncellendi")
            self.duzenle_pencere.destroy()
            self.load_masalar()
            self.masa_sec(self.secili_masa)  # Seçili masayı yenile
            
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme kaydedilemedi: {str(e)}")

    def masa_sec(self, masa_id):
        """Masa seçim işlemlerini gerçekleştirir"""
        try:
            masa = self.db.execute(
                "SELECT * FROM masalar WHERE masa_id=?",
                (masa_id,),
                fetch=True
            )
            
            if not masa:
                messagebox.showwarning("Uyarı", "Seçilen masa bulunamadı!")
                self.secili_masa = None
                return
                
            masa = masa[0]
            self.secili_masa = masa_id
            
            # Tüm butonlardan pressed state'ini kaldır
            for btn in self.masa_buttons.values():
                btn.state(['!pressed'])
            
            # Seçili butona pressed state ekle
            if masa_id in self.masa_buttons:
                self.masa_buttons[masa_id].state(['pressed'])
            
            # Bilgi panelini güncelle
            self.guncelle_bilgi_paneli(masa)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Masa bilgileri yüklenemedi: {str(e)}")
            self.secili_masa = None

    def guncelle_bilgi_paneli(self, masa):
        """Bilgi panelini günceller"""
        try:
            # Bakiye hesapla
            bakiye_result = self.db.execute(
                """SELECT COALESCE(SUM(u.fiyat * s.adet), 0) 
                FROM siparisler s JOIN urunler u ON s.urun_id = u.urun_id
                WHERE s.masa_id=? AND s.durum!='Ödendi'""",
                (masa['masa_id'],),
                fetch=True
            )
            bakiye = bakiye_result[0][0] if bakiye_result else 0.0
            
            # Bilgileri güncelle
            self.info_labels['numara'].config(text=f"Masa No: {masa['masa_no']}")
            self.info_labels['isim'].config(text=f"İsim: {masa['isim'] or '-'}")
            self.info_labels['durum'].config(text=f"Durum: {masa['durum']}")
            self.info_labels['bakiye'].config(text=f"Bakiye: {bakiye:.2f} ₺")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Bakiye hesaplanamadı: {str(e)}")

    def masa_tasi(self):
        """Masa taşıma işlemini gerçekleştirir"""
        if not self.secili_masa:
            messagebox.showwarning("Uyarı", "Önce bir masa seçmelisiniz!")
            return
            
        messagebox.showinfo("Bilgi", "Masa taşıma işlemi henüz implemente edilmedi")

    def siparis_ekle(self):
        """Sipariş ekleme işlemini başlatır"""
        if not self.secili_masa:
            messagebox.showwarning("Uyarı", "Önce bir masa seçmelisiniz!")
            return
        
        try:
            # Notebook'u bul (ana pencere)
            notebook = self.root.master
            
            # Sipariş modülünü bul
            for child in notebook.winfo_children():
                if hasattr(child, 'siparis_ekle'):
                    # Sipariş sekmesine geç
                    notebook.select(notebook.index(child))
                    # Sipariş ekleme fonksiyonunu çağır
                    child.sipariş_ekle(self.secili_masa)
                    return
            
            messagebox.showerror("Hata", "Sipariş modülü bulunamadı!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Sipariş eklenemedi: {str(e)}")