import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class PaymentTab(ttk.Frame):  # DÜZELTME: OrderTab → PaymentTab
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.current_order = None
        self._setup_ui()
    
    def _setup_ui(self):
        # Order info frame
        self.info_frame = ttk.LabelFrame(self, text="Sipariş Bilgileri")
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.info_frame, text="Sipariş No:").grid(row=0, column=0, sticky=tk.W)
        self.order_id_label = ttk.Label(self.info_frame, text="")
        self.order_id_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(self.info_frame, text="Masa No:").grid(row=1, column=0, sticky=tk.W)
        self.table_label = ttk.Label(self.info_frame, text="")
        self.table_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(self.info_frame, text="Toplam Tutar:").grid(row=2, column=0, sticky=tk.W)
        self.total_label = ttk.Label(self.info_frame, text="")
        self.total_label.grid(row=2, column=1, sticky=tk.W)
        
        # Payment details frame
        self.payment_frame = ttk.LabelFrame(self, text="Ödeme Detayları")
        self.payment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.payment_frame, text="Ödeme Yöntemi:").grid(row=0, column=0, sticky=tk.W)
        self.payment_method = ttk.Combobox(self.payment_frame, values=["Nakit", "Kredi Kartı", "Banka Kartı"])
        self.payment_method.grid(row=0, column=1)
        self.payment_method.current(0)
        
        ttk.Label(self.payment_frame, text="Ödenen Tutar:").grid(row=1, column=0, sticky=tk.W)
        self.paid_amount = ttk.Entry(self.payment_frame)
        self.paid_amount.grid(row=1, column=1)
        
        ttk.Label(self.payment_frame, text="Para Üstü:").grid(row=2, column=0, sticky=tk.W)
        self.change_label = ttk.Label(self.payment_frame, text="0.00₺")
        self.change_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Button(self.payment_frame, text="Hesapla", command=self._calculate_change).grid(row=3, column=1, sticky=tk.E)
        ttk.Button(self, text="Ödemeyi Tamamla", command=self._complete_payment).pack(pady=10)
    
    def load_order(self, order_id):
        """Sipariş bilgilerini yükler"""
        self.current_order = order_id
        order = db.execute("SELECT * FROM orders WHERE id=?", (order_id,), fetch=True)
        if order:
            order = order[0]
            self.order_id_label.config(text=order['id'])
            self.table_label.config(text=order['table_number'])
            self.total_label.config(text=f"{order['total_amount']:.2f}₺")
            self.paid_amount.delete(0, tk.END)
            self.paid_amount.insert(0, f"{order['total_amount']:.2f}")
            self._calculate_change()
    
    def _calculate_change(self):
        """Para üstünü hesaplar"""
        try:
            total = float(self.total_label['text'].replace('₺', ''))
            paid = float(self.paid_amount.get())
            change = paid - total
            self.change_label.config(text=f"{max(change, 0):.2f}₺")
        except ValueError:
            self.change_label.config(text="0.00₺")
    
    def _complete_payment(self):
        """Ödemeyi tamamlar"""
        if not self.current_order:
            messagebox.showwarning("Uyarı", "Ödenecek sipariş bulunamadı")
            return
            
        try:
            total = float(self.total_label['text'].replace('₺', ''))
            paid = float(self.paid_amount.get())
            
            if paid < total:
                messagebox.showerror("Hata", "Ödenen tutar yetersiz!")
                return
                
            db.execute("UPDATE orders SET status='paid' WHERE id=?", (self.current_order,))
            messagebox.showinfo("Başarılı", "Ödeme tamamlandı")
            self.current_order = None
            self._reset_fields()
            
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz tutar!")
    
    def _reset_fields(self):
        """Alanları sıfırlar"""
        self.order_id_label.config(text="")
        self.table_label.config(text="")
        self.total_label.config(text="")
        self.paid_amount.delete(0, tk.END)
        self.change_label.config(text="0.00₺")