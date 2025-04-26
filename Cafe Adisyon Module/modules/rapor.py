import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.database import Database
import csv

class RaporModule:
    def __init__(self, root: tk.Tk, db: Database):
        self.root = root
        self.db = db
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.setup_ui()
    
    def setup_ui(self):
        # Ana frame
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Rapor seçenekleri
        options_frame = ttk.LabelFrame(self.main_frame, text="Rapor Seçenekleri")
        options_frame.pack(fill=tk.X, pady=5)
        
        # Rapor türü
        ttk.Label(options_frame, text="Rapor Türü:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.rapor_turu_var = tk.StringVar(value="gunluk")
        rapor_turleri = ttk.Combobox(options_frame, textvariable=self.rapor_turu_var, 
                                    values=["gunluk", "haftalık", "aylık", "özel"], state="readonly")
        rapor_turleri.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        rapor_turleri.bind("<<ComboboxSelected>>", self.rapor_turu_degisti)
        
        # Tarih aralığı (özel rapor için)
        self.tarih_frame = ttk.Frame(options_frame)
        
        ttk.Label(self.tarih_frame, text="Başlangıç:").grid(row=0, column=0, padx=5, pady=5)
        self.baslangic_tarihi = ttk.Entry(self.tarih_frame, width=10)
        self.baslangic_tarihi.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.tarih_frame, text="Bitiş:").grid(row=0, column=2, padx=5, pady=5)
        self.bitis_tarihi = ttk.Entry(self.tarih_frame, width=10)
        self.bitis_tarihi.grid(row=0, column=3, padx=5, pady=5)
        
        # Bugünün tarihini varsayılan olarak ayarla
        today = datetime.now().strftime("%Y-%m-%d")
        self.baslangic_tarihi.insert(0, today)
        self.bitis_tarihi.insert(0, today)
        
        # Rapor içeriği
        ttk.Label(options_frame, text="Rapor İçeriği:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.rapor_icerik_var = tk.StringVar(value="tum_siparisler")
        ttk.Radiobutton(options_frame, text="Tüm Siparişler", variable=self.rapor_icerik_var, 
                       value="tum_siparisler").grid(row=1, column=1, padx=5, pady=5, sticky='w')
        ttk.Radiobutton(options_frame, text="Sadece Tamamlananlar", variable=self.rapor_icerik_var, 
                       value="tamamlananlar").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        
        # Butonlar
        btn_frame = ttk.Frame(options_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Rapor Oluştur", command=self.rapor_olustur).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Excel'e Aktar", command=self.excel_aktar).pack(side=tk.LEFT, padx=5)
        
        # Rapor sonuçları
        self.rapor_tree = ttk.Treeview(self.main_frame, 
                                      columns=('siparis_id', 'masa', 'musteri', 'urun', 'adet', 'tutar', 'tarih', 'durum'), 
                                      show='headings')
        self.rapor_tree.heading('siparis_id', text='Sipariş ID')
        self.rapor_tree.heading('masa', text='Masa')
        self.rapor_tree.heading('musteri', text='Müşteri')
        self.rapor_tree.heading('urun', text='Ürün')
        self.rapor_tree.heading('adet', text='Adet')
        self.rapor_tree.heading('tutar', text='Tutar')
        self.rapor_tree.heading('tarih', text='Tarih')
        self.rapor_tree.heading('durum', text='Durum')
        
        self.rapor_tree.column('siparis_id', width=70, anchor='center')
        self.rapor_tree.column('masa', width=100)
        self.rapor_tree.column('musteri', width=150)
        self.rapor_tree.column('urun', width=150)
        self.rapor_tree.column('adet', width=50, anchor='center')
        self.rapor_tree.column('tutar', width=80, anchor='e')
        self.rapor_tree.column('tarih', width=100)
        self.rapor_tree.column('durum', width=100)
        
        self.rapor_tree.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Toplam satırı
        self.toplam_frame = ttk.Frame(self.main_frame)
        self.toplam_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.toplam_frame, text="Toplam Sipariş:").pack(side=tk.LEFT, padx=5)
        self.toplam_siparis_label = ttk.Label(self.toplam_frame, text="0", font=('Arial', 10, 'bold'))
        self.toplam_siparis_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.toplam_frame, text="Toplam Tutar:").pack(side=tk.LEFT, padx=5)
        self.toplam_tutar_label = ttk.Label(self.toplam_frame, text="0.00 ₺", font=('Arial', 10, 'bold'))
        self.toplam_tutar_label.pack(side=tk.LEFT, padx=5)
    
    def rapor_turu_degisti(self, event=None):
        if self.rapor_turu_var.get() == "özel":
            self.tarih_frame.grid(row=0, column=2, columnspan=2, padx=5, pady=5)
        else:
            self.tarih_frame.grid_forget()
    
    def get_date_range(self) -> tuple:
        rapor_turu = self.rapor_turu_var.get()
        today = datetime.now()
        
        if rapor_turu == "gunluk":
            start_date = today.strftime("%Y-%m-%d")
            end_date = start_date
        elif rapor_turu == "haftalık":
            start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        elif rapor_turu == "aylık":
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
        else:  # özel
            start_date = self.baslangic_tarihi.get()
            end_date = self.bitis_tarihi.get()
        
        return start_date, end_date
    
    def rapor_olustur(self):
        try:
            start_date, end_date = self.get_date_range()
            rapor_icerik = self.rapor_icerik_var.get()
            
            query = """SELECT s.siparis_id, m.masa_adi, 
                       CASE WHEN mu.musteri_id IS NULL THEN '-' ELSE mu.ad || ' ' || COALESCE(mu.soyad, '') END as musteri,
                       u.urun_adi, s.adet, u.fiyat * s.adet as tutar, 
                       s.tarih, s.durum
                       FROM siparisler s
                       LEFT JOIN masalar m ON s.masa_id = m.masa_id
                       LEFT JOIN musteriler mu ON s.musteri_id = mu.musteri_id
                       LEFT JOIN urunler u ON s.urun_id = u.urun_id
                       WHERE date(s.tarih) BETWEEN ? AND ?"""
            
            params = [start_date, end_date]
            
            if rapor_icerik == "tamamlananlar":
                query += " AND s.durum = 'Tamamlandı'"
            
            query += " ORDER BY s.tarih DESC"
            
            siparisler = self.db.execute(query, params, fetch=True)
            
            self.rapor_tree.delete(*self.rapor_tree.get_children())
            
            toplam_tutar = 0.0
            for siparis in siparisler:
                self.rapor_tree.insert('', tk.END, values=(
                    siparis['siparis_id'],
                    siparis['masa_adi'],
                    siparis['musteri'],
                    siparis['urun_adi'],
                    siparis['adet'],
                    f"{siparis['tutar']:.2f} ₺",
                    siparis['tarih'].split()[0] if siparis['tarih'] else "-",
                    siparis['durum']
                ))
                toplam_tutar += siparis['tutar']
            
            self.toplam_siparis_label.config(text=str(len(siparisler)))
            self.toplam_tutar_label.config(text=f"{toplam_tutar:.2f} ₺")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı: {e}")
    
    def excel_aktar(self):
        if not self.rapor_tree.get_children():
            messagebox.showwarning("Uyarı", "Önce rapor oluşturmalısınız!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Dosyaları", "*.csv"), ("Tüm Dosyalar", "*.*")],
            title="Raporu Kaydet"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Başlıklar
                headers = [self.rapor_tree.heading(col)['text'] for col in self.rapor_tree['columns']]
                writer.writerow(headers)
                
                # Veriler
                for child in self.rapor_tree.get_children():
                    row = self.rapor_tree.item(child)['values']
                    writer.writerow(row)
                
                # Toplam satırı
                writer.writerow([])
                writer.writerow(["Toplam Sipariş:", self.toplam_siparis_label.cget('text')])
                writer.writerow(["Toplam Tutar:", self.toplam_tutar_label.cget('text')])
            
            messagebox.showinfo("Başarılı", f"Rapor başarıyla kaydedildi:\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor kaydedilemedi: {e}")