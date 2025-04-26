import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict
from core.models import Urun, Kategori
from core.database import Database

class UrunModule:
    def __init__(self, root: tk.Tk, db: Database):
        self.root = root
        self.db = db
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.kategoriler = self.load_kategoriler()
        self.setup_ui()
        self.load_urunler()
    
    def setup_ui(self):
        # Ana frame
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ürün listesi
        self.tree = ttk.Treeview(self.main_frame, 
                                columns=('urun_id', 'urun_adi', 'fiyat', 'kategori', 'stok'), 
                                show='headings')
        self.tree.heading('urun_id', text='ID')
        self.tree.heading('urun_adi', text='Ürün Adı')
        self.tree.heading('fiyat', text='Fiyat')
        self.tree.heading('kategori', text='Kategori')
        self.tree.heading('stok', text='Stok')
        self.tree.column('urun_id', width=50, anchor='center')
        self.tree.column('urun_adi', width=200)
        self.tree.column('fiyat', width=80, anchor='e')
        self.tree.column('kategori', width=150)
        self.tree.column('stok', width=60, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Kontrol butonları
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_ekle = ttk.Button(btn_frame, text="Ürün Ekle", command=self.urun_ekle_form)
        self.btn_ekle.pack(side=tk.LEFT, padx=5)
        
        self.btn_guncelle = ttk.Button(btn_frame, text="Ürün Güncelle", command=self.urun_guncelle_form)
        self.btn_guncelle.pack(side=tk.LEFT, padx=5)
        
        self.btn_sil = ttk.Button(btn_frame, text="Ürün Sil", command=self.urun_sil)
        self.btn_sil.pack(side=tk.LEFT, padx=5)
        
        self.btn_kategori = ttk.Button(btn_frame, text="Kategori Yönetimi", command=self.kategori_yonetimi)
        self.btn_kategori.pack(side=tk.LEFT, padx=5)
    
    def load_kategoriler(self) -> List[Dict]:
        return self.db.execute("SELECT * FROM kategoriler ORDER BY kategori_adi", fetch=True) or []
    
    def load_urunler(self):
        self.tree.delete(*self.tree.get_children())
        query = """SELECT u.urun_id, u.urun_adi, u.fiyat, k.kategori_adi, u.stok 
                   FROM urunler u LEFT JOIN kategoriler k ON u.kategori_id = k.kategori_id
                   ORDER BY u.urun_adi"""
        urunler = self.db.execute(query, fetch=True)
        for urun in urunler:
            self.tree.insert('', tk.END, values=(
                urun['urun_id'],
                urun['urun_adi'],
                f"{urun['fiyat']:.2f} ₺",
                urun['kategori_adi'] or "-",
                urun['stok']
            ))
    
    def urun_ekle_form(self):
        self.ekle_pencere = tk.Toplevel(self.root)
        self.ekle_pencere.title("Ürün Ekle")
        
        # Ürün Adı
        ttk.Label(self.ekle_pencere, text="Ürün Adı:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_urun_adi = ttk.Entry(self.ekle_pencere, width=30)
        self.entry_urun_adi.grid(row=0, column=1, padx=5, pady=5)
        
        # Fiyat
        ttk.Label(self.ekle_pencere, text="Fiyat:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_fiyat = ttk.Entry(self.ekle_pencere, width=30)
        self.entry_fiyat.grid(row=1, column=1, padx=5, pady=5)
        
        # Kategori
        ttk.Label(self.ekle_pencere, text="Kategori:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.kategori_var = tk.StringVar()
        self.combo_kategori = ttk.Combobox(
            self.ekle_pencere, 
            textvariable=self.kategori_var,
            values=[k['kategori_adi'] for k in self.kategoriler],
            state='readonly'
        )
        self.combo_kategori.grid(row=2, column=1, padx=5, pady=5)
        
        # Stok
        ttk.Label(self.ekle_pencere, text="Stok:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.entry_stok = ttk.Entry(self.ekle_pencere, width=30)
        self.entry_stok.insert(0, "0")
        self.entry_stok.grid(row=3, column=1, padx=5, pady=5)
        
        # Butonlar
        btn_frame = ttk.Frame(self.ekle_pencere)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Ekle", command=self.urun_ekle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.ekle_pencere.destroy).pack(side=tk.LEFT, padx=5)
    
    def urun_ekle(self):
        try:
            urun_adi = self.entry_urun_adi.get().strip()
            fiyat = float(self.entry_fiyat.get().replace(',', '.'))
            stok = int(self.entry_stok.get())
            kategori_adi = self.kategori_var.get()
            
            if not urun_adi:
                raise ValueError("Ürün adı boş olamaz")
            if fiyat <= 0:
                raise ValueError("Fiyat pozitif olmalıdır")
            if stok < 0:
                raise ValueError("Stok negatif olamaz")
            
            kategori_id = None
            if kategori_adi:
                kategori = next((k for k in self.kategoriler if k['kategori_adi'] == kategori_adi), None)
                if not kategori:
                    raise ValueError("Geçersiz kategori seçimi")
                kategori_id = kategori['kategori_id']
            
            self.db.execute(
                "INSERT INTO urunler (urun_adi, fiyat, kategori_id, stok) VALUES (?, ?, ?, ?)",
                (urun_adi, fiyat, kategori_id, stok)
            )
            
            messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi!")
            self.ekle_pencere.destroy()
            self.load_urunler()
            
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Ürün eklenemedi: {e}")
    
    def urun_guncelle_form(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin!")
            return
        
        urun_data = self.tree.item(selected)['values']
        self.guncelle_pencere = tk.Toplevel(self.root)
        self.guncelle_pencere.title("Ürün Güncelle")
        
        # Ürün ID (gizli)
        self.urun_id = urun_data[0]
        
        # Ürün Adı
        ttk.Label(self.guncelle_pencere, text="Ürün Adı:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_urun_adi = ttk.Entry(self.guncelle_pencere, width=30)
        self.entry_urun_adi.insert(0, urun_data[1])
        self.entry_urun_adi.grid(row=0, column=1, padx=5, pady=5)
        
        # Fiyat
        ttk.Label(self.guncelle_pencere, text="Fiyat:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_fiyat = ttk.Entry(self.guncelle_pencere, width=30)
        self.entry_fiyat.insert(0, urun_data[2].replace(' ₺', ''))
        self.entry_fiyat.grid(row=1, column=1, padx=5, pady=5)
        
        # Kategori
        ttk.Label(self.guncelle_pencere, text="Kategori:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.kategori_var = tk.StringVar(value=urun_data[3] if urun_data[3] != '-' else '')
        self.combo_kategori = ttk.Combobox(
            self.guncelle_pencere, 
            textvariable=self.kategori_var,
            values=[k['kategori_adi'] for k in self.kategoriler],
            state='readonly'
        )
        self.combo_kategori.grid(row=2, column=1, padx=5, pady=5)
        
        # Stok
        ttk.Label(self.guncelle_pencere, text="Stok:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.entry_stok = ttk.Entry(self.guncelle_pencere, width=30)
        self.entry_stok.insert(0, urun_data[4])
        self.entry_stok.grid(row=3, column=1, padx=5, pady=5)
        
        # Butonlar
        btn_frame = ttk.Frame(self.guncelle_pencere)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Güncelle", command=self.urun_guncelle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.guncelle_pencere.destroy).pack(side=tk.LEFT, padx=5)
    
    def urun_guncelle(self):
        try:
            urun_adi = self.entry_urun_adi.get().strip()
            fiyat = float(self.entry_fiyat.get().replace(',', '.'))
            stok = int(self.entry_stok.get())
            kategori_adi = self.kategori_var.get()
            
            if not urun_adi:
                raise ValueError("Ürün adı boş olamaz")
            if fiyat <= 0:
                raise ValueError("Fiyat pozitif olmalıdır")
            if stok < 0:
                raise ValueError("Stok negatif olamaz")
            
            kategori_id = None
            if kategori_adi:
                kategori = next((k for k in self.kategoriler if k['kategori_adi'] == kategori_adi), None)
                if not kategori:
                    raise ValueError("Geçersiz kategori seçimi")
                kategori_id = kategori['kategori_id']
            
            self.db.execute(
                "UPDATE urunler SET urun_adi=?, fiyat=?, kategori_id=?, stok=? WHERE urun_id=?",
                (urun_adi, fiyat, kategori_id, stok, self.urun_id)
            )
            
            messagebox.showinfo("Başarılı", "Ürün başarıyla güncellendi!")
            self.guncelle_pencere.destroy()
            self.load_urunler()
            
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Ürün güncellenemedi: {e}")
    
    def urun_sil(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin!")
            return
        
        urun_id = self.tree.item(selected)['values'][0]
        urun_adi = self.tree.item(selected)['values'][1]
        
        if messagebox.askyesno("Onay", f"{urun_adi} adlı ürünü silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!"):
            try:
                self.db.execute("DELETE FROM urunler WHERE urun_id=?", (urun_id,))
                messagebox.showinfo("Başarılı", "Ürün başarıyla silindi!")
                self.load_urunler()
            except Exception as e:
                messagebox.showerror("Hata", f"Ürün silinemedi: {e}")
    
    def kategori_yonetimi(self):
        self.kategori_pencere = tk.Toplevel(self.root)
        self.kategori_pencere.title("Kategori Yönetimi")
        
        # Kategori listesi
        self.kategori_tree = ttk.Treeview(self.kategori_pencere, columns=('kategori_id', 'kategori_adi'), show='headings')
        self.kategori_tree.heading('kategori_id', text='ID')
        self.kategori_tree.heading('kategori_adi', text='Kategori Adı')
        self.kategori_tree.column('kategori_id', width=50, anchor='center')
        self.kategori_tree.column('kategori_adi', width=200)
        self.kategori_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Kontrol butonları
        btn_frame = ttk.Frame(self.kategori_pencere)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, text="Yeni Kategori", command=self.kategori_ekle_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Kategori Sil", command=self.kategori_sil).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Kapat", command=self.kategori_pencere.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.load_kategori_listesi()
    
    def load_kategori_listesi(self):
        self.kategori_tree.delete(*self.kategori_tree.get_children())
        for kategori in self.kategoriler:
            self.kategori_tree.insert('', tk.END, values=(kategori['kategori_id'], kategori['kategori_adi']))
    
    def kategori_ekle_form(self):
        self.kategori_ekle_pencere = tk.Toplevel(self.kategori_pencere)
        self.kategori_ekle_pencere.title("Yeni Kategori")
        
        ttk.Label(self.kategori_ekle_pencere, text="Kategori Adı:").pack(pady=5)
        self.entry_kategori_adi = ttk.Entry(self.kategori_ekle_pencere, width=30)
        self.entry_kategori_adi.pack(pady=5)
        
        btn_frame = ttk.Frame(self.kategori_ekle_pencere)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Ekle", command=self.kategori_ekle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.kategori_ekle_pencere.destroy).pack(side=tk.LEFT, padx=5)
    
    def kategori_ekle(self):
        kategori_adi = self.entry_kategori_adi.get().strip()
        if not kategori_adi:
            messagebox.showerror("Hata", "Kategori adı boş olamaz!")
            return
        
        try:
            self.db.execute("INSERT INTO kategoriler (kategori_adi) VALUES (?)", (kategori_adi,))
            messagebox.showinfo("Başarılı", "Kategori başarıyla eklendi!")
            self.kategoriler = self.load_kategoriler()
            self.load_kategori_listesi()
            self.kategori_ekle_pencere.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kategori adı zaten kayıtlı!")
    
    def kategori_sil(self):
        selected = self.kategori_tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir kategori seçin!")
            return
        
        kategori_id = self.kategori_tree.item(selected)['values'][0]
        kategori_adi = self.kategori_tree.item(selected)['values'][1]
        
        # Kategoriye bağlı ürün kontrolü
        urunler = self.db.execute(
            "SELECT COUNT(*) as count FROM urunler WHERE kategori_id=?", 
            (kategori_id,), 
            fetch=True
        )
        
        if urunler and urunler[0]['count'] > 0:
            messagebox.showerror(
                "Hata", 
                f"Bu kategoriye bağlı {urunler[0]['count']} ürün var!\n"
                "Önce bu ürünleri silin veya başka kategoriye taşıyın."
            )
            return
        
        if messagebox.askyesno("Onay", f"{kategori_adi} adlı kategoriyi silmek istediğinize emin misiniz?"):
            try:
                self.db.execute("DELETE FROM kategoriler WHERE kategori_id=?", (kategori_id,))
                messagebox.showinfo("Başarılı", "Kategori başarıyla silindi!")
                self.kategoriler = self.load_kategoriler()
                self.load_kategori_listesi()
            except Exception as e:
                messagebox.showerror("Hata", f"Kategori silinemedi: {e}")