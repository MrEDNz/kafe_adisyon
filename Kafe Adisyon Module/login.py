import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class LoginWindow:
    def __init__(self, parent, on_success_callback):
        self.parent = parent
        self.on_success = on_success_callback
        
        self.frame = ttk.Frame(parent, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        
        # Enter tuşu desteği
        parent.bind('<Return>', lambda e: self.authenticate())
    
    def create_widgets(self):
        """Arayüz bileşenlerini oluşturur"""
        # Başlık
        ttk.Label(
            self.frame, 
            text="Kafe Adisyon Sistemi", 
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))
        
        # Kullanıcı adı
        ttk.Label(self.frame, text="Kullanıcı Adı:").pack(anchor="w")
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.pack(fill=tk.X, pady=5)
        self.username_entry.focus_set()
        
        # Şifre
        ttk.Label(self.frame, text="Şifre:").pack(anchor="w")
        self.password_entry = ttk.Entry(self.frame, show="•")
        self.password_entry.pack(fill=tk.X, pady=5)
        
        # Giriş butonu
        ttk.Button(
            self.frame, 
            text="Giriş Yap", 
            command=self.authenticate,
            style='Accent.TButton'
        ).pack(pady=20)
    
    def authenticate(self, event=None):
        """Kullanıcı doğrulama işlemi"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror(
                "Hata", 
                "Lütfen kullanıcı adı ve şifre girin!",
                parent=self.parent
            )
            return
            
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
            fetch=True
        )
        
        if user:
            self.on_success(user[0])
        else:
            messagebox.showerror(
                "Hata", 
                "Geçersiz kullanıcı adı veya şifre!",
                parent=self.parent
            )
            self.password_entry.delete(0, tk.END)