# constants.py

# --- Sabit Tanımlamalar ---

# Veritabanı dosyasının adı
DB_NAME = 'cafe_adisyon.db'

# Masa Durumları ve Renkleri İçin Stiller (main.py'deki stil tanımlarıyla uyumlu)
MASA_STYLES = {
    'Boş': {
        'bg': '#d4edda',       # Açık yeşil arka plan
        'fg': '#040404',       # Koyu yeşil yazı rengi
        'active_bg': '#c3e6cb' # Mouse üzerine gelince biraz daha açık yeşil
    },
    'Dolu': {
        'bg': '#f8d7da',       # Açık kırmızı arka plan
        'fg': '#721c24',       # Koyu kırmızı yazı rengi
        'active_bg': '#f5c6cb' # Mouse üzerine gelince biraz daha açık kırmızı
    },
    'Ödeme Bekliyor': {
        'bg': '#fff3cd',       # Açık sarı arka plan
        'fg': '#856404',       # Koyu sarı yazı rengi
        'active_bg': '#ffeeba' # Üzerine gelince biraz daha açık sarı
    },
    'Geçikmiş': { # Geçikmiş masa stili
        'bg': '#dc3545',       # Kırmızı arka plan
        'fg': '#ffffff',       # Beyaz yazı rengi
        'active_bg': '#c82333' # Üzerine gelince daha koyu kırmızı
    },
}

# Kategoriye özel hızlı satış butonu renkleri (Adisyon sekmesi için)
# Pastel renkler ve ürün türüne uygun tonlar kullanıldı
# Bu renkler main.py'de stil olarak tanımlanacaktır.
CATEGORY_COLORS = {
    'Sıcak Kahveler': {
        'bg': '#f5e6cc',       # Açık kahverengi (kahve tonu)
        'fg': '#4a2a00',       # Koyu kahverengi
        'active_bg': '#e8d5b0' # Üzerine gelince biraz daha koyu
    },
    'Soğuk Kahveler': {
        'bg': '#d4f1f9',       # Açık buz mavisi (soğuk ton)
        'fg': '#004d66',       # Koyu mavi/yeşil
        'active_bg': '#b8e7f2' # Üzerine gelince biraz daha koyu
    },
    'Soğuk İçecekler': {
        'bg': '#cce5ff',       # Açık pastel mavi
        'fg': '#004085',       # Koyu mavi
        'active_bg': '#b3d7ff' # Üzerine gelince biraz daha koyu
    },
    'Sıcak İçecekler': {
        'bg': '#f8d7da',       # Açık pastel pembe/kırmızı (sıcak ton)
        'fg': '#721c24',       # Koyu kırmızı
        'active_bg': '#f5c6cb' # Üzerine gelince biraz daha koyu
    },
    'Frappe': {
        'bg': '#e2e3e5',       # Açık gri (nötr ton)
        'fg': '#41464b',       # Koyu gri
        'active_bg': '#d3d6db' # Üzerine gelince biraz daha koyu
    },
    'Diğer': {
        'bg': '#dae0e5',       # Orta gri
        'fg': '#383d41',       # Çok koyu gri
        'active_bg': '#c8ced3' # Üzerine gelince biraz daha koyu
    },
    'Tatlılar': {
        'bg': '#f0e3f0',       # Açık pastel mor
        'fg': '#5a325a',       # Koyu mor
        'active_bg': '#e6d0e6' # Üzerine gelince biraz daha koyu
    },
    'Milk Shake Çeşitleri': {
        'bg': '#fcf8e3',       # Çok açık sarı (süt/krema tonu)
        'fg': '#8a6d3b',       # Koyu sarı/kahve
        'active_bg': '#faebcc' # Üzerine gelince biraz daha koyu
    },
    'Diğer Kahveler': {
        'bg': '#d6d8d9',       # Orta açık gri (nötr kahve tonu)
        'fg': '#1b1e21',       # Çok koyu gri
        'active_bg': '#c6c8ca' # Üzerine gelince biraz daha koyu
    },
    # Diğer kategoriler buraya eklenebilir
}

# Varsayılan Kategoriler (Veritabanı ilk oluşturulduğunda eklenir)
DEFAULT_CATEGORIES = [
    'Soğuk İçecekler', 'Frappe', 'Tatlılar', 'Sıcak Kahveler',
    'Soğuk Kahveler', 'Diğer', 'Sıcak İçecekler',
    'Milk Shake Çeşitleri', 'Diğer Kahveler'
]

# Varsayılan Ürünler (Ad, Fiyat, Kategori Adı, Aktif Durum (1/0), Hızlı Satış Sırası)
# Veritabanı ilk oluşturulduğunda eklenir.
DEFAULT_PRODUCTS = [
    ('Espresso', 110.00, 'Sıcak Kahveler', 1, 1),
    ('Doppio', 120.00, 'Sıcak Kahveler', 1, 2),
    ('Espresso Mocchiato', 90.00, 'Sıcak Kahveler', 1, 3),
    ('Americano', 90.00, 'Sıcak Kahveler', 1, 4),
    ('Cappucino', 110.00, 'Sıcak Kahveler', 1, 5),
    ('Latte', 90.00, 'Sıcak Kahveler', 1, 6),
    ('Flat White', 90.00, 'Sıcak Kahveler', 1, 7),
    ('Cortado', 90.00, 'Sıcak Kahveler', 1, 8),
    ('Mocha', 110.00, 'Sıcak Kahveler', 1, 9),
    ('Caramel Mocchiato', 110.00, 'Sıcak Kahveler', 1, 10),
    ('White Mocha', 110.00, 'Sıcak Kahveler', 1, 11),
    ('Tuffee Nut Latte', 90.00, 'Sıcak Kahveler', 1, 12),
    ('Filtre Kahve', 90.00, 'Sıcak Kahveler', 1, 13),
    ('Filtre Kahve Sütlü', 90.00, 'Sıcak Kahveler', 1, 14),
    ('Sıcak Çikolata', 100.00, 'Sıcak İçecekler', 1, 15),
    ('Ice Latte', 90.00, 'Soğuk Kahveler', 1, 16),
    ('Ice Latte Costom', 90.00, 'Soğuk Kahveler', 1, 17),
    ('Ice Mocha', 90.00, 'Soğuk Kahveler', 1, 18),
    ('Ice Americano', 90.00, 'Soğuk Kahveler', 1, 19),
    ('Ice White Mocca', 90.00, 'Soğuk Kahveler', 1, 20),
    ('Ice Filtre Kahve', 90.00, 'Soğuk Kahveler', 1, 21),
    ('Ice Karamel Mocha', 110.00, 'Soğuk Kahveler', 1, 22),
    ('Ice Tuffee Nut Latte', 100.00, 'Soğuk Kahveler', 1, 23),
    ('Cool Lime', 120.00, 'Milk Shake Çeşitleri', 1, 24),
    ('Limonata', 120.00, 'Milk Shake Çeşitleri', 1, 25),
    ('Karadut Suyu', 120.00, 'Milk Shake Çeşitleri', 1, 26),
    ('Çilekli Milk Shake', 120.00, 'Milk Shake Çeşitleri', 1, 27),
    ('Kırmızı Orman Milk Shake', 120.00, 'Milk Shake Çeşitleri', 1, 28),
    ('Böğürtlen Milk Shake', 120.00, 'Milk Shake Çeşitleri', 1, 29),
    ('Kara Orman Milk Shake', 120.00, 'Milk Shake Çeşitleri', 1, 30),
    ('Oreolu Frappe', 130.00, 'Frappe', 1, 31),
    ('Çikolatalı Frappe', 130.00, 'Frappe', 1, 32),
    ('Vanilyalı Frappe', 130.00, 'Frappe', 1, 33),
    ('Karamelli Frappe', 130.00, 'Frappe', 1, 34),
    ('Çilekli Smoothie', 130.00, 'Frappe', 1, 35),
    ('Muzlu Smoothie', 130.00, 'Frappe', 1, 36),
    ('Coca Kola', 60.00, 'Soğuk İçecekler', 1, 37),
    ('Fanta', 60.00, 'Soğuk İçecekler', 1, 38),
    ('Sprite', 60.00, 'Soğuk İçecekler', 1, 39),
    ('İce Tea Çeşitleri', 60.00, 'Soğuk İçecekler', 1, 40),
    ('Soda Sade', 40.00, 'Soğuk İçecekler', 1, 41),
    ('Meyveli Soda', 30.00, 'Soğuk İçecekler', 1, 42),
    ('Su', 30.00, 'Soğuk İçecekler', 1, 43),
    ('Churchill', 60.00, 'Soğuk İçecekler', 1, 44),
    ('Türk Kahvesi', 80.00, 'Diğer Kahveler', 1, 45),
    ('Menengiç Kahvesi', 80.00, 'Diğer Kahveler', 1, 46),
    ('Dibek Kahvesi', 80.00, 'Diğer Kahveler', 1, 47),
    ('Detox Kahve', 80.00, 'Diğer Kahveler', 1, 48),
    ('Çay', 30.00, 'Sıcak İçecekler', 1, 49),
    ('Ihlamur', 40.00, 'Sıcak İçecekler', 1, 50),
    ('Yeşilçay', 40.00, 'Sıcak İçecekler', 1, 51),
    ('Hibiskus', 40.00, 'Sıcak İçecekler', 1, 52),
    ('Adaçayı', 40.00, 'Sıcak İçecekler', 1, 53),
    ('San Sebastian', 80.00, 'Tatlılar', 1, 54),
    ('Yaban Mersinli Cheesecake', 60.00, 'Tatlılar', 1, 55),
    ('Farmbuazlı Cheesecake', 60.00, 'Tatlılar', 1, 56),
    ('Strawberry Roll Cake', 60.00, 'Tatlılar', 1, 57),
    ('Marlenka', 60.00, 'Tatlılar', 1, 58),
    ('Mangolia Çilek – Lotus – Oreo', 60.00, 'Tatlılar', 1, 59),
    ('Alman Pastası', 60.00, 'Tatlılar', 1, 60),
    ('Tramisu', 60.00, 'Tatlılar', 1, 61),
    ('Berliner', 60.00, 'Tatlılar', 1, 62),
    ('Kruvasan', 60.00, 'Tatlılar', 1, 63),
    # Pasif örnek ürün
    ('Eski Ürün (Pasif)', 1.00, 'Diğer', 0, 0),
]

# Geçikmiş masa kontrol süresi (milisaniye cinsinden)
LATE_TABLE_CHECK_INTERVAL_MS = 60000 # Her 1 dakikada bir kontrol et
LATE_TABLE_THRESHOLD_MINUTES = 30 # 30 dakika

# Yeni kategoriye renk ataması için varsayılan renk paleti (constants.py içinde yönetilebilir)
DEFAULT_CATEGORY_COLORS = [
    '#ffadad', '#ffd6a5', '#fdffb6', '#caffbf', '#9bf6ff',
    '#a0c4ff', '#bdb2ff', '#ffc6ff', '#fffffc', '#f28482'
]

# Geçmiş verileri arşivleme süresi (yıl cinsinden)
ARCHIVE_PERIOD_YEARS = 1