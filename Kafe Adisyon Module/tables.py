import tkinter as tk
from tkinter import ttk, messagebox
from database import db_execute  # execute_query yerine db_execute kullanıyoruz

class TablesTab(ttk.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self._setup_ui()
        self._load_tables()
    
    def _setup_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="Masa Ekle", command=self._add_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Masa Sil", command=self._delete_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Yenile", command=self._load_tables).pack(side=tk.RIGHT, padx=5)
        
        # Masaları gösterim
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Masa durum renkleri
        self.status_colors = {
            'available': 'green',
            'occupied': 'red',
            'reserved': 'orange'
        }
    
    def _load_tables(self):
        """Masaları veritabanından yükler"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
        tables = db_execute("SELECT * FROM tables ORDER BY table_number", fetch=True)
        
        if not tables:
            ttk.Label(self.table_frame, text="Tanımlı masa bulunamadı").pack(pady=50)
            return
            
        # Masaları grid olarak göster
        for i, table in enumerate(tables):
            frame = ttk.LabelFrame(
                self.table_frame,
                text=f"Masa {table['table_number']}",
                width=150,
                height=150
            )
            frame.grid(row=i//4, column=i%4, padx=10, pady=10, sticky="nsew")
            frame.pack_propagate(False)
            
            # Masa bilgileri
            ttk.Label(frame, text=f"Kapasite: {table['capacity']}").pack()
            
            # Durum göstergesi
            status_frame = ttk.Frame(frame)
            status_frame.pack(pady=5)
            ttk.Label(
                status_frame, 
                text=table['status'].upper(),
                foreground=self.status_colors.get(table['status'], 'black')
            ).pack(side=tk.LEFT)
            
            # Kontrol butonları
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(pady=5)
            
            ttk.Button(
                btn_frame, 
                text="Sipariş Aç", 
                command=lambda t=table: self._open_order(t),
                width=10
            ).pack(side=tk.LEFT, padx=2)
            
            ttk.Button(
                btn_frame, 
                text="Rezerve Et", 
                command=lambda t=table: self._reserve_table(t),
                width=10
            ).pack(side=tk.LEFT, padx=2)
    
    def _add_table(self):
        """Yeni masa ekler"""
        dialog = tk.Toplevel(self)
        dialog.title("Yeni Masa Ekle")
        
        ttk.Label(dialog, text="Masa No:").grid(row=0, column=0, padx=5, pady=5)
        table_no_entry = ttk.Entry(dialog)
        table_no_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Kapasite:").grid(row=1, column=0, padx=5, pady=5)
        capacity_entry = ttk.Entry(dialog)
        capacity_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save_table():
            try:
                db_execute(
                    "INSERT INTO tables (table_number, capacity) VALUES (?, ?)",
                    (int(table_no_entry.get()), int(capacity_entry.get()))
                )
                self._load_tables()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Hata", f"Masa eklenemedi: {e}")
        
        ttk.Button(dialog, text="Kaydet", command=save_table).grid(row=2, column=1, pady=10)
    
    def _delete_table(self):
        """Masa siler"""
        # Implementasyon eklenebilir
        pass
    
    def _open_order(self, table):
        """Masa için sipariş açar - DÜZELTİLMİŞ KISIM"""
        if table['status'] == 'occupied':
            messagebox.showinfo("Bilgi", "Bu masa zaten dolu!")
            return
            
        # Masa durumunu güncelle
        db_execute(
            "UPDATE tables SET status='occupied' WHERE id=?",
            (table['id'],)
        )
        
        # Sipariş sekmesine geçiş için event gönder
        self.event_generate("<<TableSelected>>", data={
            'table_id': table['id'],
            'table_number': table['table_number']
        })
        self._load_tables()
    
    def _reserve_table(self, table):
        """Masayı rezerve eder"""
        db_execute(
            "UPDATE tables SET status='reserved' WHERE id=?",
            (table['id'],)
        )
        self._load_tables()