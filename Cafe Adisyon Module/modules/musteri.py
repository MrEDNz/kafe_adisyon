import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
from core.database import Database
from core.models import Musteri

class MusteriModule:
    def __init__(self, root: tk.Tk, db: Database):
        """Müşteri yönetimi modülü başlatıcısı"""
        self.root = root
        self.db = db
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.setup_ui()
        self.load_musteriler()
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluşturur"""
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Müşteri listesi için Treeview
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=('id', 'ad', 'soyad', 'telefon', 'eposta', 'kayit_tarihi'),
            show='headings',
            selectmode='browse'
        )
        
        # Sütun başlıkları
        self.tree.heading('id', text='ID')
        self.tree.heading('ad', text='Ad')
        self.tree.heading('soyad', text='Soyad')
        self.tree.heading('telefon', text='Telefon')
        self.tree.heading('eposta', text='E-posta')
        self.tree.heading('kayit_tarihi', text='Kayıt Tarihi')
        
        # Sütun genişlikleri
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('ad', width=120, anchor='w')
        self.tree.column('soyad', width=120, anchor='w')
        self.tree.column('telefon', width=120, anchor='w')
        self.tree.column('eposta', width=180, anchor='w')
        self.tree.column('kayit_tarihi', width=120, anchor='center')
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar ekleme
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buton çerçevesi
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # Butonlar
        self.btn_ekle = ttk.Button(btn_frame, text="Yeni Müşteri", command=self.musteri_ekle_form)
        self.btn_ekle.pack(side=tk.LEFT, padx=5)
        
        self.btn_guncelle = ttk.Button(btn_frame, text="Düzenle", command=self.musteri_guncelle_form)
        self.btn_guncelle.pack(side=tk.LEFT, padx=5)
        
        self.btn_sil = ttk.Button(btn_frame, text="Sil", command=self.musteri_sil)
        self.btn_sil.pack(side=tk.LEFT, padx=5)
        
        # Arama çerçevesi
        arama_frame = ttk.Frame(self.main_frame)
        arama_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(arama_frame, text="Ara:").pack(side=tk.LEFT, padx=5)
        self.arama_var = tk.StringVar()
        self.entry_arama = ttk.Entry(arama_frame, textvariable=self.arama_var, width=30)
        self.entry_arama.pack(side=tk.LEFT, padx=5)
        self.entry_arama.bind('<KeyRelease>', lambda e: self.load_musteriler())
        
        ttk.Button(arama_frame, text="Temizle", command=self.arama_temizle).pack(side=tk.LEFT, padx=5)
    
    def load_musteriler(self):
        """Veritabanından müşterileri yükler ve listeler"""
        try:
            self.tree.delete(*self.tree.get_children())
            arama_metni = self.arama_var.get().strip()
            
            if arama_metni:
                query = """SELECT * FROM musteriler 
                          WHERE ad LIKE ? OR soyad LIKE ? OR telefon LIKE ? OR eposta LIKE ?
                          ORDER BY ad, soyad"""
                params = (f"%{arama_metni}%",) * 4
            else:
                query = "SELECT * FROM musteriler ORDER BY ad, soyad"
                params = ()
            
            musteriler = self.db.execute(query, params, fetch=True)
            
            for musteri in musteriler:
                kayit_tarihi = musteri['kayit_tarihi'].split()[0] if musteri['kayit_tarihi'] else "-"
                self.tree.insert('', 'end', values=(
                    musteri['musteri_id'],
                    musteri['ad'],
                    musteri['soyad'] or "-",
                    musteri['telefon'] or "-",
                    musteri['eposta'] or "-",
                    kayit_tarihi
                ))
                
        except Exception as e:
            messagebox.showerror("Hata", f"Müşteriler yüklenemedi: {str(e)}")
    
    def musteri_ekle_form(self):
        """Yeni müşteri ekleme formunu açar"""
        self.ekle_pencere = tk.Toplevel(self.root)
        self.ekle_pencere.title("Yeni Müşteri")
        self.ekle_pencere.resizable(False, False)
        
        # Form alanları
        fields = [
            ("Ad*:", 'entry_ad'),
            ("Soyad:", 'entry_soyad'),
            ("Telefon:", 'entry_telefon'),
            ("E-posta:", 'entry_eposta')
        ]
        
        for i, (label_text, attr_name) in enumerate(fields):
            ttk.Label(self.ekle_pencere, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(self.ekle_pencere, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, attr_name, entry)
        
        # Butonlar
        btn_frame = ttk.Frame(self.ekle_pencere)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Kaydet", command=self.musteri_ekle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.ekle_pencere.destroy).pack(side=tk.LEFT, padx=5)
    
    def musteri_ekle(self):
        """Yeni müşteriyi veritabanına kaydeder"""
        try:
            ad = self.entry_ad.get().strip()
            soyad = self.entry_soyad.get().strip() or None
            telefon = self.entry_telefon.get().strip() or None
            eposta = self.entry_eposta.get().strip() or None
            
            if not ad:
                raise ValueError("Ad alanı zorunludur")
            
            if telefon and not telefon.isdigit():
                raise ValueError("Telefon sadece rakamlardan oluşmalıdır")
            
            self.db.execute(
                "INSERT INTO musteriler (ad, soyad, telefon, eposta) VALUES (?, ?, ?, ?)",
                (ad, soyad, telefon, eposta)
            )
            
            messagebox.showinfo("Başarılı", "Müşteri başarıyla eklendi!")
            self.ekle_pencere.destroy()
            self.load_musteriler()
            
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Müşteri eklenemedi: {str(e)}")
    
    def musteri_guncelle_form(self):
        """Müşteri düzenleme formunu açar"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir müşteri seçin!")
            return
        
        musteri_data = self.tree.item(selected)['values']
        self.guncelle_pencere = tk.Toplevel(self.root)
        self.guncelle_pencere.title("Müşteri Düzenle")
        self.guncelle_pencere.resizable(False, False)
        
        self.secilen_musteri_id = musteri_data[0]
        
        # Form alanları
        fields = [
            ("Ad*:", 'entry_ad', musteri_data[1]),
            ("Soyad:", 'entry_soyad', musteri_data[2] if musteri_data[2] != "-" else ""),
            ("Telefon:", 'entry_telefon', musteri_data[3] if musteri_data[3] != "-" else ""),
            ("E-posta:", 'entry_eposta', musteri_data[4] if musteri_data[4] != "-" else "")
        ]
        
        for i, (label_text, attr_name, default_value) in enumerate(fields):
            ttk.Label(self.guncelle_pencere, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(self.guncelle_pencere, width=30)
            entry.insert(0, default_value)
            entry.grid(row=i, column=1, padx=5, pady=5)
            setattr(self, attr_name, entry)
        
        # Butonlar
        btn_frame = ttk.Frame(self.guncelle_pencere)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Güncelle", command=self.musteri_guncelle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.guncelle_pencere.destroy).pack(side=tk.LEFT, padx=5)
    
    def musteri_guncelle(self):
        """Müşteri bilgilerini günceller"""
        try:
            ad = self.entry_ad.get().strip()
            soyad = self.entry_soyad.get().strip() or None
            telefon = self.entry_telefon.get().strip() or None
            eposta = self.entry_eposta.get().strip() or None
            
            if not ad:
                raise ValueError("Ad alanı zorunludur")
            
            if telefon and not telefon.isdigit():
                raise ValueError("Telefon sadece rakamlardan oluşmalıdır")
            
            self.db.execute(
                """UPDATE musteriler 
                SET ad=?, soyad=?, telefon=?, eposta=? 
                WHERE musteri_id=?""",
                (ad, soyad, telefon, eposta, self.secilen_musteri_id)
            )
            
            messagebox.showinfo("Başarılı", "Müşteri bilgileri güncellendi!")
            self.guncelle_pencere.destroy()
            self.load_musteriler()
            
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {str(e)}")
        except Exception as e:
            messagebox.showerror("Hata", f"Güncelleme başarısız: {str(e)}")
    
    def musteri_sil(self):
        """Seçili müşteriyi siler"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir müşteri seçin!")
            return
        
        musteri_id = self.tree.item(selected)['values'][0]
        musteri_ad = self.tree.item(selected)['values'][1]
        
        # Müşteriye ait sipariş kontrolü
        siparis_sayisi = self.db.execute(
            "SELECT COUNT(*) as sayi FROM siparisler WHERE musteri_id=?",
            (musteri_id,),
            fetch=True
        )[0]['sayi']
        
        if siparis_sayisi > 0:
            messagebox.showerror(
                "Hata", 
                f"Bu müşteriye ait {siparis_sayisi} sipariş bulunuyor!\n"
                "Müşteriyi silemezsiniz."
            )
            return
        
        if messagebox.askyesno(
            "Onay", 
            f"{musteri_ad} isimli müşteriyi silmek istediğinize emin misiniz?\n"
            "Bu işlem geri alınamaz!"
        ):
            try:
                self.db.execute(
                    "DELETE FROM musteriler WHERE musteri_id=?",
                    (musteri_id,)
                )
                messagebox.showinfo("Başarılı", "Müşteri başarıyla silindi!")
                self.load_musteriler()
            except Exception as e:
                messagebox.showerror("Hata", f"Silme işlemi başarısız: {str(e)}")
    
    def arama_temizle(self):
        """Arama kutusunu temizler ve tüm müşterileri yükler"""
        self.arama_var.set("")
        self.load_musteriler()