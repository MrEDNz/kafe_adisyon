# menu.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class MenuTab(ttk.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self._setup_ui()
        self._load_menu_items()
    
    def _setup_ui(self):
        # Treeview for menu items
        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Ürün Adı")
        self.tree.heading("Category", text="Kategori")
        self.tree.heading("Price", text="Fiyat")
        self.tree.heading("Stock", text="Stok")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Ekle", command=self._add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Düzenle", command=self._edit_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Sil", command=self._delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Yenile", command=self._load_menu_items).pack(side=tk.RIGHT, padx=5)
    
    def _load_menu_items(self):
        """Menü öğelerini veritabanından yükler"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        items = db.execute("SELECT * FROM menu_items", fetch=True)
        if items:
            for item in items:
                self.tree.insert("", tk.END, values=(
                    item['id'],
                    item['name'],
                    item['category'],
                    f"{item['price']:.2f}₺",
                    item['stock']
                ))
    
    def _add_item(self):
        """Yeni menü öğesi ekler"""
        self._show_item_dialog()
    
    def _edit_item(self):
        """Seçili öğeyi düzenler"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir öğe seçin")
            return
            
        item_id = self.tree.item(selected[0])['values'][0]
        self._show_item_dialog(item_id)
    
    def _delete_item(self):
        """Seçili öğeyi siler"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir öğe seçin")
            return
            
        item_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Onay", "Bu öğeyi silmek istediğinize emin misiniz?"):
            db.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
            self._load_menu_items()
    
    def _show_item_dialog(self, item_id=None):
        """Öğe ekleme/düzenleme diyaloğunu gösterir"""
        dialog = tk.Toplevel(self)
        dialog.title("Menü Öğesi" if not item_id else "Öğe Düzenle")
        dialog.resizable(False, False)
        
        # Form alanları
        ttk.Label(dialog, text="Ürün Adı:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Kategori:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        category_entry = ttk.Entry(dialog)
        category_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Fiyat:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Stok:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        stock_entry = ttk.Entry(dialog)
        stock_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Eğer düzenleme modundaysak, verileri yükle
        if item_id:
            item = db.execute("SELECT * FROM menu_items WHERE id=?", (item_id,), fetch=True)
            if item:
                item = item[0]
                name_entry.insert(0, item['name'])
                category_entry.insert(0, item['category'])
                price_entry.insert(0, str(item['price']))
                stock_entry.insert(0, str(item['stock']))
        
        # Kaydet butonu
        def save_item():
            try:
                data = (
                    name_entry.get(),
                    category_entry.get(),
                    float(price_entry.get()),
                    int(stock_entry.get())
                )
                
                if item_id:  # Update existing
                    db.execute(
                        "UPDATE menu_items SET name=?, category=?, price=?, stock=? WHERE id=?",
                        (*data, item_id)
                    )
                else:  # Insert new
                    db.execute(
                        "INSERT INTO menu_items (name, category, price, stock) VALUES (?, ?, ?, ?)",
                        data
                    )
                
                dialog.destroy()
                self._load_menu_items()
            except ValueError:
                messagebox.showerror("Hata", "Geçersiz veri girişi!")
        
        ttk.Button(dialog, text="Kaydet", command=save_item).grid(row=4, column=1, padx=5, pady=10, sticky=tk.E)