# config.py
import tkinter.ttk as ttk

# AYARLAR (CLASS İÇİNDE DEĞİL)
DB_PATH = "cafe.db"
THEME = "clam"
WINDOW_TITLE = "Cafe Adisyon Programı"
WINDOW_SIZE = "1200x700"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
CURRENCY_SYMBOL = "₺"
DEFAULT_SIPARIS_DURUM = "Hazırlanıyor"
ODEME_TURLERI = ["Nakit", "Kredi Kartı", "Banka Kartı"]

def configure_styles():
    """Tüm stil ayarlarını yapar"""
    style = ttk.Style()
    
    # Temel stiller
    style.configure('TFrame', background='#f0f0f0')
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10), padding=5)
    
    # Masa durum renkleri
    style.configure('Dolu.TButton', foreground='white', background='#d9534f')  # Kırmızı
    style.configure('Rezerve.TButton', foreground='white', background='#f0ad4e')  # Turuncu
    style.configure('Bos.TButton', foreground='white', background='#5cb85c')  # Yeşil
    
    # Notebook ayarları
    style.configure('TNotebook', tabposition='n')
    style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10, 'bold'))
    
    # Treeview stili
    style.configure('Treeview', rowheight=25)
    style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    return style  # Style nesnesini döndür