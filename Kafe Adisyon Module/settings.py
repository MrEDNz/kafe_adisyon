# settings.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class SettingsTab(ttk.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self._setup_ui()
        self._load_users()
    
    def _setup_ui(self):
        # Users list
        self.tree = ttk.Treeview(self, columns=("ID", "Username", "Role"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Username", text="Kullanıcı Adı")
        self.tree.heading("Role", text="Rol")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Kullanıcı Ekle", command=self._add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Kullanıcı Düzenle", command=self._edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Kullanıcı Sil", command=self._delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Yenile", command=self._load_users).pack(side=tk.RIGHT, padx=5)
    
    def _load_users(self):
        """Kullanıcıları yükler"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        users = db.execute("SELECT id, username, role FROM users", fetch=True)
        if users:
            for user in users:
                self.tree.insert("", tk.END, values=(
                    user['id'],
                    user['username'],
                    user['role']
                ))
    
    def _add_user(self):
        """Yeni kullanıcı ekler"""
        self._show_user_dialog()
    
    def _edit_user(self):
        """Kullanıcı düzenler"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir kullanıcı seçin")
            return
            
        user_id = self.tree.item(selected[0])['values'][0]
        self._show_user_dialog(user_id)
    
    def _delete_user(self):
        """Kullanıcı siler"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kullanıcı seçin")
            return
            
        user_id = self.tree.item(selected[0])['values'][0]
        
        # Admin kullanıcılarını silmeyi engelle
        user = db.execute("SELECT role FROM users WHERE id=?", (user_id,), fetch=True)
        if user and user[0]['role'] == 'admin':
            messagebox.showerror("Hata", "Admin kullanıcıları silinemez!")
            return
            
        if messagebox.askyesno("Onay", "Bu kullanıcıyı silmek istediğinize emin misiniz?"):
            db.execute("DELETE FROM users WHERE id=?", (user_id,))
            self._load_users()
    
    def _show_user_dialog(self, user_id=None):
        """Kullanıcı ekleme/düzenleme diyaloğunu gösterir"""
        dialog = tk.Toplevel(self)
        dialog.title("Yeni Kullanıcı" if not user_id else "Kullanıcı Düzenle")
        dialog.resizable(False, False)
        
        # Form fields
        ttk.Label(dialog, text="Kullanıcı Adı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        username_entry = ttk.Entry(dialog)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Şifre:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Rol:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        role_combobox = ttk.Combobox(dialog, values=["admin", "user"], state="readonly")
        role_combobox.grid(row=2, column=1, padx=5, pady=5)
        role_combobox.current(1)  # Default to 'user'
        
        # If editing, load user data
        if user_id:
            user = db.execute("SELECT * FROM users WHERE id=?", (user_id,), fetch=True)
            if user:
                user = user[0]
                username_entry.insert(0, user['username'])
                role_combobox.set(user['role'])
        
        def save_user():
            username = username_entry.get()
            password = password_entry.get()
            role = role_combobox.get()
            
            if not username or not role:
                messagebox.showerror("Hata", "Kullanıcı adı ve rol gereklidir!")
                return
                
            if not user_id and not password:
                messagebox.showerror("Hata", "Yeni kullanıcı için şifre gereklidir!")
                return
                
            try:
                if user_id:  # Update
                    if password:
                        db.execute(
                            "UPDATE users SET username=?, password=?, role=? WHERE id=?",
                            (username, password, role, user_id)
                        )
                    else:
                        db.execute(
                            "UPDATE users SET username=?, role=? WHERE id=?",
                            (username, role, user_id)
                        )
                else:  # Insert
                    db.execute(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        (username, password, role)
                    )
                
                dialog.destroy()
                self._load_users()
            except sqlite3.IntegrityError:
                messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış!")
        
        ttk.Button(dialog, text="Kaydet", command=save_user).grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)