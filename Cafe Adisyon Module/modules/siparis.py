import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from core.database import Database
from core.models import Siparis

class SiparisModule:
    def __init__(self, root: tk.Tk, db: Database):
        self.root = root
        self.db = db
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.masalar = self.load_masalar()
        self.urunler = self.load_urunler()
        self.musteriler = self.load_musteriler()
        self.setup_ui()
        self.load_acik_siparisler()
        self.secili_masa = None
    
    def masa_sec(self, masa_id):
        self.secili_masa = masa_id
        self.load_siparisler()
        
        # UI'da seçili masayı göster
        masa = self.db.execute(
            "SELECT masa_no, isim FROM masalar WHERE masa_id=?",
            (masa_id,),
            fetch=True
        )[0]
        
        self.masa_label.config(
            text=f"Seçili Masa: {masa['masa_no']} - {masa['isim'] or ''}"
        )
    
    def urun_sec(self, urun_id):
        if not self.secili_masa:
            messagebox.showwarning("Uyarı", "Önce bir masa seçmelisiniz!")
            return

    def setup_ui(self):
        # Ana frame
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sipariş listesi
        self.tree = ttk.Treeview(self.main_frame, 
                                columns=('siparis_id', 'masa', 'musteri', 'urun', 'adet', 'tutar', 'tarih', 'durum'), 
                                show='headings')
        self.tree.heading('siparis_id', text='ID')
        self.tree.heading('masa', text='Masa')
        self.tree.heading('musteri', text='Müşteri')
        self.tree.heading('urun', text='Ürün')
        self.tree.heading('adet', text='Adet')
        self.tree.heading('tutar', text='Tutar')
        self.tree.heading('tarih', text='Tarih')
        self.tree.heading('durum', text='Durum')
        
        self.tree.column('siparis_id', width=50, anchor='center')
        self.tree.column('masa', width=100)
        self.tree.column('musteri', width=150)
        self.tree.column('urun', width=150)
        self.tree.column('adet', width=50, anchor='center')
        self.tree.column('tutar', width=80, anchor='e')
        self.tree.column('tarih', width=100)
        self.tree.column('durum', width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Kontrol butonları
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_yeni = ttk.Button(btn_frame, text="Yeni Sipariş", command=self.yeni_siparis_form)
        self.btn_yeni.pack(side=tk.LEFT, padx=5)
        
        self.btn_guncelle = ttk.Button(btn_frame, text="Durum Güncelle", command=self.durum_guncelle)
        self.btn_guncelle.pack(side=tk.LEFT, padx=5)
        
        self.btn_sil = ttk.Button(btn_frame, text="Sipariş Sil", command=self.siparis_sil)
        self.btn_sil.pack(side=tk.LEFT, padx=5)
        
        self.btn_odeme = ttk.Button(btn_frame, text="Ödeme Al", command=self.odeme_al)
        self.btn_odeme.pack(side=tk.LEFT, padx=5)
    
    def load_masalar(self) -> List[Dict]:
        return self.db.execute("SELECT * FROM masalar ORDER BY masa_adi", fetch=True) or []
    
    def load_urunler(self) -> List[Dict]:
        return self.db.execute("""
            SELECT u.urun_id, u.urun_adi, u.fiyat, k.kategori_adi 
            FROM urunler u LEFT JOIN kategoriler k ON u.kategori_id = k.kategori_id
            ORDER BY u.urun_adi
        """, fetch=True) or []
    
    def load_musteriler(self) -> List[Dict]:
        return self.db.execute("SELECT * FROM musteriler ORDER BY ad, soyad", fetch=True) or []
    
    def load_acik_siparisler(self):
        self.tree.delete(*self.tree.get_children())
        query = """SELECT s.siparis_id, m.masa_adi, 
                   CASE WHEN mu.musteri_id IS NULL THEN '-' ELSE mu.ad || ' ' || COALESCE(mu.soyad, '') END as musteri,
                   u.urun_adi, s.adet, u.fiyat * s.adet as tutar, 
                   s.tarih, s.durum
                   FROM siparisler s
                   LEFT JOIN masalar m ON s.masa_id = m.masa_id
                   LEFT JOIN musteriler mu ON s.musteri_id = mu.musteri_id
                   LEFT JOIN urunler u ON s.urun_id = u.urun_id
                   WHERE s.durum != 'Tamamlandı'
                   ORDER BY s.tarih DESC"""
        
        siparisler = self.db.execute(query, fetch=True)
        for siparis in siparisler:
            self.tree.insert('', tk.END, values=(
                siparis['siparis_id'],
                siparis['masa_adi'],
                siparis['musteri'],
                siparis['urun_adi'],
                siparis['adet'],
                f"{siparis['tutar']:.2f} ₺",
                siparis['tarih'].split()[0] if siparis['tarih'] else "-",
                siparis['durum']
            ))
    
    def yeni_siparis_form(self):
        self.siparis_pencere = tk.Toplevel(self.root)
        self.siparis_pencere.title("Yeni Sipariş")
        
        # Masa seçimi
        ttk.Label(self.siparis_pencere, text="Masa:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.masa_var = tk.StringVar()
        self.combo_masa = ttk.Combobox(
            self.siparis_pencere, 
            textvariable=self.masa_var,
            values=[m['masa_adi'] for m in self.masalar],
            state='readonly'
        )
        self.combo_masa.grid(row=0, column=1, padx=5, pady=5)
        
        # Müşteri seçimi
        ttk.Label(self.siparis_pencere, text="Müşteri:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.musteri_var = tk.StringVar()
        self.combo_musteri = ttk.Combobox(
            self.siparis_pencere, 
            textvariable=self.musteri_var,
            values=[f"{m['ad']} {m['soyad'] or ''}" for m in self.musteriler],
            state='readonly'
        )
        self.combo_musteri.grid(row=1, column=1, padx=5, pady=5)
        self.combo_musteri.set('-')
        
        # Ürün seçimi
        ttk.Label(self.siparis_pencere, text="Ürün:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.urun_var = tk.StringVar()
        self.combo_urun = ttk.Combobox(
            self.siparis_pencere, 
            textvariable=self.urun_var,
            values=[f"{u['urun_adi']} ({u['kategori_adi'] or '-'}) - {u['fiyat']:.2f}₺" for u in self.urunler],
            state='readonly'
        )
        self.combo_urun.grid(row=2, column=1, padx=5, pady=5)
        
        # Adet
        ttk.Label(self.siparis_pencere, text="Adet:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.spin_adet = ttk.Spinbox(self.siparis_pencere, from_=1, to=20, width=5)
        self.spin_adet.set(1)
        self.spin_adet.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Notlar
        ttk.Label(self.siparis_pencere, text="Notlar:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.entry_notlar = ttk.Entry(self.siparis_pencere)
        self.entry_notlar.grid(row=4, column=1, padx=5, pady=5)
        
        # Butonlar
        btn_frame = ttk.Frame(self.siparis_pencere)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Kaydet", command=self.siparis_ekle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="İptal", command=self.siparis_pencere.destroy).pack(side=tk.LEFT, padx=5)
    
    def siparis_ekle(self):
        try:
            # Masa seçimi
            masa_adi = self.masa_var.get()
            if not masa_adi:
                raise ValueError("Masa seçimi zorunludur")
            
            masa = next((m for m in self.masalar if m['masa_adi'] == masa_adi), None)
            if not masa:
                raise ValueError("Geçersiz masa seçimi")
            
            # Müşteri seçimi
            musteri_id = None
            musteri_adi = self.musteri_var.get()
            if musteri_adi and musteri_adi != '-':
                musteri = next((m for m in self.musteriler 
                               if f"{m['ad']} {m['soyad'] or ''}" == musteri_adi), None)
                if not musteri:
                    raise ValueError("Geçersiz müşteri seçimi")
                musteri_id = musteri['musteri_id']
            
            # Ürün seçimi
            urun_text = self.urun_var.get()
            if not urun_text:
                raise ValueError("Ürün seçimi zorunludur")
            
            # Ürün adını ayıklama (combobox formatı: "Ürün Adı (Kategori) - Fiyat")
            urun_adi = urun_text.split(' - ')[0].split(' (')[0]
            urun = next((u for u in self.urunler if u['urun_adi'] == urun_adi), None)
            if not urun:
                raise ValueError("Geçersiz ürün seçimi")
            
            # Adet
            adet = int(self.spin_adet.get())
            if adet < 1:
                raise ValueError("Adet en az 1 olmalıdır")
            
            # Notlar
            notlar = self.entry_notlar.get().strip() or None
            
            # Siparişi kaydet
            self.db.execute(
                """INSERT INTO siparisler 
                (masa_id, musteri_id, urun_id, adet, durum, notlar) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (masa['masa_id'], musteri_id, urun['urun_id'], adet, 'Hazırlanıyor', notlar)
            )  # <-- Bu parantez kapatma önemli
            
            # Masayı dolu olarak işaretle
            self.db.execute(
                "UPDATE masalar SET durum = 'Dolu' WHERE masa_id = ?",
                (masa['masa_id'],)
            )  # <-- Bu da doğru

            messagebox.showinfo("Başarılı", "Sipariş başarıyla eklendi!")
            self.siparis_pencere.destroy()
            self.load_acik_siparisler()
            
        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Sipariş eklenemedi: {e}")
    
    def durum_guncelle(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir sipariş seçin!")
            return
        
        siparis_id = self.tree.item(selected)['values'][0]
        current_durum = self.tree.item(selected)['values'][7]
        
        durum_pencere = tk.Toplevel(self.root)
        durum_pencere.title("Sipariş Durumu Güncelle")
        
        ttk.Label(durum_pencere, text="Yeni Durum:").pack(pady=5)
        
        durum_var = tk.StringVar(value=current_durum)
        ttk.Combobox(durum_pencere, textvariable=durum_var, 
                    values=["Hazırlanıyor", "Servis Edildi", "Tamamlandı"], 
                    state="readonly").pack(pady=5)
        
        def update():
            new_durum = durum_var.get()
            self.db.execute(
                "UPDATE siparisler SET durum = ? WHERE siparis_id = ?",
                (new_durum, siparis_id)
            )
            
            # Eğer sipariş tamamlandıysa, masa durumunu kontrol et
            if new_durum == "Tamamlandı":
                self.masa_durum_guncelle(siparis_id)
            
            messagebox.showinfo("Başarılı", "Sipariş durumu güncellendi!")
            durum_pencere.destroy()
            self.load_acik_siparisler()
        
        ttk.Button(durum_pencere, text="Güncelle", command=update).pack(pady=5)
    
    def masa_durum_guncelle(self, siparis_id: int):
        # Siparişin masa ID'sini al
        masa = self.db.execute(
            "SELECT masa_id FROM siparisler WHERE siparis_id = ?",
            (siparis_id,),
            fetch=True
        )
        
        if masa and masa[0]['masa_id']:
            # Bu masada başka açık sipariş var mı kontrol et
            acik_siparis = self.db.execute(
                """SELECT COUNT(*) as count FROM siparisler 
                WHERE masa_id = ? AND durum != 'Tamamlandı'""",
                (masa[0]['masa_id'],),
                fetch=True
            )
            
            # Eğer başka açık sipariş yoksa masayı boş yap
            if acik_siparis and acik_siparis[0]['count'] == 0:
                self.db.execute(
                    "UPDATE masalar SET durum = 'Boş' WHERE masa_id = ?",
                    (masa[0]['masa_id'],)
                )
    
    def siparis_sil(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir sipariş seçin!")
            return
        
        siparis_id = self.tree.item(selected)['values'][0]
        urun_adi = self.tree.item(selected)['values'][3]
        
        if messagebox.askyesno("Onay", f"{urun_adi} adlı siparişi silmek istediğinize emin misiniz?"):
            try:
                # Önce siparişin masa ID'sini al
                masa = self.db.execute(
                    "SELECT masa_id FROM siparisler WHERE siparis_id = ?",
                    (siparis_id,),
                    fetch=True
                )
                
                # Siparişi sil
                self.db.execute(
                    "DELETE FROM siparisler WHERE siparis_id = ?",
                    (siparis_id,)
                )
                
                # Eğer bu masada başka açık sipariş yoksa masayı boş yap
                if masa and masa[0]['masa_id']:
                    self.masa_durum_guncelle(siparis_id)
                
                messagebox.showinfo("Başarılı", "Sipariş başarıyla silindi!")
                self.load_acik_siparisler()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Sipariş silinemedi: {e}")
    
    def odeme_al(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir sipariş seçin!")
            return
        
        siparis_id = self.tree.item(selected)['values'][0]
        masa_adi = self.tree.item(selected)['values'][1]
        tutar = float(self.tree.item(selected)['values'][5].replace(' ₺', ''))
        
        odeme_pencere = tk.Toplevel(self.root)
        odeme_pencere.title(f"Ödeme Al - Masa: {masa_adi}")
        
        # Tutar bilgisi
        ttk.Label(odeme_pencere, text=f"Tutar: {tutar:.2f} ₺", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Ödeme türü
        ttk.Label(odeme_pencere, text="Ödeme Türü:").pack()
        odeme_turu_var = tk.StringVar(value="Nakit")
        ttk.Combobox(odeme_pencere, textvariable=odeme_turu_var, 
                     values=["Nakit", "Kredi Kartı", "Banka Kartı"], 
                     state="readonly").pack(pady=5)
        
        # İndirim
        ttk.Label(odeme_pencere, text="İndirim (%):").pack()
        self.indirim_var = tk.StringVar(value="0")
        ttk.Entry(odeme_pencere, textvariable=self.indirim_var, width=5).pack()
        
        # Ödenen tutar
        ttk.Label(odeme_pencere, text="Ödenen Tutar:").pack()
        self.odenen_var = tk.StringVar(value=f"{tutar:.2f}")
        ttk.Entry(odeme_pencere, textvariable=self.odenen_var).pack(pady=5)
        
        def odeme_yap():
            try:
                indirim = float(self.indirim_var.get())
                odenen = float(self.odenen_var.get())
                
                if indirim < 0 or indirim > 100:
                    raise ValueError("İndirim %0-100 arasında olmalıdır")
                
                if odenen <= 0:
                    raise ValueError("Ödenen tutar pozitif olmalıdır")
                
                # Sipariş durumunu güncelle
                self.db.execute(
                    "UPDATE siparisler SET durum = 'Tamamlandı' WHERE siparis_id = ?",
                    (siparis_id,)
                )
                
                # Masa durumunu güncelle
                self.masa_durum_guncelle(siparis_id)
                
                # Ödeme kaydı (basit versiyon)
                self.db.execute(
                    """INSERT INTO odemeler 
                    (siparis_id, odeme_turu, indirim, odenen_tutar, tarih) 
                    VALUES (?, ?, ?, ?, datetime('now'))""",
                    (siparis_id, odeme_turu_var.get(), indirim, odenen)
                )
                
                messagebox.showinfo("Başarılı", f"Ödeme alındı!\nPara Üstü: {odenen - (tutar * (1 - indirim/100)):.2f} ₺")
                odeme_pencere.destroy()
                self.load_acik_siparisler()
                
            except ValueError as e:
                messagebox.showerror("Hata", f"Geçersiz veri: {e}")
            except Exception as e:
                messagebox.showerror("Hata", f"Ödeme işlemi başarısız: {e}")
        
        ttk.Button(odeme_pencere, text="Ödemeyi Tamamla", command=odeme_yap).pack(pady=10)