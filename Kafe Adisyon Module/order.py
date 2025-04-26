import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class OrderTab(ttk.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.current_table = None
        self.current_order = None
        self._setup_ui()

    def _setup_ui(self):
        # Masa bilgi paneli
        self.table_frame = ttk.LabelFrame(self, text="Masa Bilgisi")
        self.table_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.table_info = ttk.Label(self.table_frame, text="Lütfen bir masa seçiniz", font=('Arial', 10))
        self.table_info.pack(pady=5)
        
        # Kontrol butonları
        btn_frame = ttk.Frame(self.table_frame)
        btn_frame.pack(pady=5)
        
        self.new_order_btn = ttk.Button(btn_frame, text="Yeni Sipariş", command=self._create_order, state=tk.DISABLED)
        self.new_order_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Masa Değiştir", command=self._change_table).pack(side=tk.LEFT, padx=5)
        
        # Sipariş detayları
        self.detail_frame = ttk.Frame(self)
        self.detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.order_tree = ttk.Treeview(self.detail_frame, columns=("product", "qty", "price", "total"), show="headings", height=10)
        self.order_tree.heading("product", text="Ürün Adı")
        self.order_tree.heading("qty", text="Adet")
        self.order_tree.heading("price", text="Birim Fiyat")
        self.order_tree.heading("total", text="Toplam")
        self.order_tree.pack(fill=tk.BOTH, expand=True)
        
        # Ürün ekleme paneli
        self.add_item_frame = ttk.LabelFrame(self.detail_frame, text="Ürün Ekle")
        self.add_item_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.add_item_frame, text="Ürün:").grid(row=0, column=0, padx=5)
        self.product_combo = ttk.Combobox(self.add_item_frame, state="readonly")
        self.product_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.add_item_frame, text="Adet:").grid(row=0, column=2, padx=5)
        self.qty_entry = ttk.Entry(self.add_item_frame, width=5)
        self.qty_entry.grid(row=0, column=3, padx=5)
        self.qty_entry.insert(0, "1")
        
        ttk.Button(self.add_item_frame, text="Ekle", command=self._add_item).grid(row=0, column=4, padx=5)
        
        # Ödeme butonu
        ttk.Button(self.detail_frame, text="Ödemeye Geç", command=self._proceed_to_payment).pack(pady=10)

    def load_table(self, table_data):
        """Masayı yükler ve ilgili siparişi açar"""
        self.current_table = table_data
        self.table_info.config(text=f"Masa No: {table_data['table_number']} | Durum: {table_data['status']}")
        
        order = db.execute(
            "SELECT id FROM orders WHERE table_id=? AND status='open'",
            (table_data['id'],),
            fetch=True
        )
        
        if order:
            self.current_order = order[0]['id']
            self._load_order_items()
            self.new_order_btn.config(state=tk.DISABLED)
        else:
            self.current_order = None
            self.order_tree.delete(*self.order_tree.get_children())
            self.new_order_btn.config(state=tk.NORMAL)
        
        self._update_product_combo()

    def _update_product_combo(self):
        """Ürün combobox'ını günceller"""
        products = db.execute("SELECT id, name, price FROM menu_items WHERE stock > 0", fetch=True)
        self.product_combo['values'] = [f"{p['id']} - {p['name']} ({p['price']}₺)" for p in products]
        if products:
            self.product_combo.current(0)

    def _create_order(self):
        """Yeni sipariş oluşturur"""
        if not self.current_table:
            messagebox.showwarning("Uyarı", "Lütfen önce bir masa seçin")
            return
            
        try:
            self.current_order = db.execute(
                "INSERT INTO orders (table_id, status) VALUES (?, 'open')",
                (self.current_table['id'],)
            )
            self.new_order_btn.config(state=tk.DISABLED)
            messagebox.showinfo("Başarılı", "Yeni sipariş oluşturuldu")
        except Exception as e:
            messagebox.showerror("Hata", f"Sipariş oluşturulamadı: {e}")

    def _load_order_items(self):
        """Sipariş öğelerini yükler"""
        self.order_tree.delete(*self.order_tree.get_children())
        items = db.execute('''
            SELECT mi.name, oi.quantity, oi.price 
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE oi.order_id=?
        ''', (self.current_order,), fetch=True)
        
        for item in items:
            total = item['quantity'] * item['price']
            self.order_tree.insert("", tk.END, values=(
                item['name'],
                item['quantity'],
                f"{item['price']:.2f}₺",
                f"{total:.2f}₺"
            ))

    def _add_item(self):
        """Siparişe ürün ekler"""
        if not self.current_order:
            messagebox.showwarning("Uyarı", "Önce sipariş oluşturmalısınız")
            return
            
        try:
            product_id = int(self.product_combo.get().split(" - ")[0])
            quantity = int(self.qty_entry.get())
            
            if quantity <= 0:
                messagebox.showerror("Hata", "Geçersiz adet!")
                return
                
            product = db.execute(
                "SELECT price, stock FROM menu_items WHERE id=?",
                (product_id,),
                fetch=True
            )
            
            if not product:
                messagebox.showerror("Hata", "Ürün bulunamadı!")
                return
                
            product = product[0]
            
            if quantity > product['stock']:
                messagebox.showerror("Hata", "Yetersiz stok!")
                return
                
            db.execute(
                "INSERT INTO order_items (order_id, menu_item_id, quantity, price) VALUES (?, ?, ?, ?)",
                (self.current_order, product_id, quantity, product['price'])
            )
            
            db.execute(
                "UPDATE menu_items SET stock=stock-? WHERE id=?",
                (quantity, product_id)
            )
            
            db.execute('''
                UPDATE orders SET total_amount=(
                    SELECT SUM(quantity*price) 
                    FROM order_items 
                    WHERE order_id=?
                )
                WHERE id=?
            ''', (self.current_order, self.current_order))
            
            self._load_order_items()
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, "1")
            
        except (ValueError, IndexError) as e:
            messagebox.showerror("Hata", f"Geçersiz giriş: {e}")

    def _change_table(self):
        """Masa değiştirme işlemi"""
        self.event_generate("<<ChangeTable>>")

    def _proceed_to_payment(self):
        """Ödeme ekranına geçiş"""
        if not self.current_order:
            messagebox.showwarning("Uyarı", "Önce sipariş oluşturmalısınız")
            return
            
        total = db.execute(
            "SELECT total_amount FROM orders WHERE id=?",
            (self.current_order,),
            fetch=True
        )
        
        if total and total[0]['total_amount'] > 0:
            self.event_generate("<<ProceedToPayment>>", data=self.current_order)
        else:
            messagebox.showwarning("Uyarı", "Siparişte ürün bulunmuyor")