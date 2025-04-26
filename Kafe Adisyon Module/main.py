import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db
from tables import TablesTab  # Artık çalışacak
from login import LoginWindow
from menu import MenuTab
from order import OrderTab
from payment import PaymentTab
from settings import SettingsTab

class CafeApp:
    def __init__(self):
        # Sadece bir Tk instance'ı oluştur
        self.root = tk.Tk()
        self.root.withdraw()  # Ana pencereyi tamamen gizle
        
        # Giriş penceresini oluştur
        self.show_login()
        
        # Ana döngüyü başlat
        self.root.mainloop()
    
    def show_login(self):
        """Giriş penceresini modal dialog olarak gösterir"""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Kafe Adisyon - Giriş")
        self.login_window.geometry("350x250")
        self.login_window.resizable(False, False)
        
        # Pencereyi merkeze al
        self._center_window(self.login_window)
        
        # LoginWindow'u oluştur
        self.login_screen = LoginWindow(
            self.login_window, 
            self.on_login_success
        )
        
        # Giriş penceresi kapatılırsa uygulamayı sonlandır
        self.login_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Modal dialog özelliği
        self.login_window.grab_set()
        self.login_window.focus_force()
    
    def on_login_success(self, user_data):
        """Başarılı giriş sonrası ana arayüzü oluşturur"""
        self.user_data = user_data
        self.login_window.destroy()
        
        # Ana pencereyi göster
        self.root.deiconify()
        self.root.title(f"Cafe Adisyon - {user_data['username']}")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Ana arayüz bileşenlerini oluştur
        self.setup_main_interface()
    
    def setup_main_interface(self):
        """Ana arayüz bileşenlerini oluşturur"""
        # Notebook (sekmeler) oluştur
        self.notebook = ttk.Notebook(self.root)
        
        # Tüm sekmeleri oluştur
        self.tabs = {
            "Menü": MenuTab(self.notebook, self.user_data),
            "Sipariş": OrderTab(self.notebook, self.user_data),
            "Ödeme": PaymentTab(self.notebook, self.user_data),
            "Ayarlar": SettingsTab(self.notebook, self.user_data)
        }
        
        # Sekmeleri notebook'a ekle
        for name, tab in self.tabs.items():
            self.notebook.add(tab, text=name)
        
        self.notebook.pack(expand=True, fill="both")
        
        # Sekmeler arası iletişimi kur
        self.setup_tab_communication()
    
    def setup_main_interface(self):
        """Ana arayüz bileşenlerini oluşturur"""
        self.notebook = ttk.Notebook(self.root)
        
        # Tüm sekmeleri oluştur (MASALAR yeni eklendi)
        self.tabs = {
            "Masalar": TablesTab(self.notebook, self.user_data),
            "Menü": MenuTab(self.notebook, self.user_data),
            "Sipariş": OrderTab(self.notebook, self.user_data),
            "Ödeme": PaymentTab(self.notebook, self.user_data),
            "Ayarlar": SettingsTab(self.notebook, self.user_data)
        }
        
        # Sekmeler arası iletişim
        self.tabs["Masalar"].bind("<<TableSelected>>", self.on_table_selected)
        self.tabs["Sipariş"].bind("<<ProceedToPayment>>", self.on_proceed_to_payment)

    def setup_tab_communication(self):
        """Sekmeler arası iletişimi ayarlar"""
        self.tabs["Sipariş"].bind(
            "<<ProceedToPayment>>", 
            lambda e: self.on_proceed_to_payment(e)
        )
    
    def on_proceed_to_payment(self, event):
        """Ödeme sekmesine geçiş yapar"""
        self.tabs["Ödeme"].load_order(event.data)
        self.notebook.select(self.tabs["Ödeme"])
    
    def quit_app(self):
        """Uygulamayı tamamen kapatır"""
        self.root.quit()
    
    def _center_window(self, window):
        """Pencereyi ekranın ortasına yerleştirir"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'+{x}+{y}')

if __name__ == "__main__":
    initialize_database()  # Tablolar oluşturulur

if __name__ == "__main__":
    # Test verilerini yükle
    try:
        from tests.initialize_test_data import initialize_test_data
        initialize_test_data()
    except Exception as e:
        print(f"Test verileri yüklenemedi: {e}")
    
    # Uygulamayı başlat
    app = CafeApp()