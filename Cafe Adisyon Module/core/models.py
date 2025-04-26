from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Masa:
    masa_id: Optional[int] = None
    masa_adi: str = ""
    durum: str = "Boş"
    
    def __post_init__(self):
        if not self.masa_adi:
            raise ValueError("Masa adı boş olamaz")

@dataclass
class Kategori:
    kategori_id: Optional[int] = None
    kategori_adi: str = ""
    
    def __post_init__(self):
        if not self.kategori_adi:
            raise ValueError("Kategori adı boş olamaz")

@dataclass
class Urun:
    urun_id: Optional[int] = None
    urun_adi: str = ""
    fiyat: float = 0.0
    kategori_id: Optional[int] = None
    stok: int = 0
    
    def __post_init__(self):
        if not self.urun_adi:
            raise ValueError("Ürün adı boş olamaz")
        if self.fiyat < 0:
            raise ValueError("Fiyat negatif olamaz")

@dataclass
class Musteri:
    musteri_id: Optional[int] = None
    ad: str = ""
    soyad: str = ""
    telefon: str = ""
    eposta: str = ""
    kayit_tarihi: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.ad:
            raise ValueError("Müşteri adı boş olamaz")

@dataclass
class Odeme:
    odeme_id: Optional[int] = None
    siparis_id: int = 0
    odeme_turu: str = "Nakit"
    indirim: float = 0.0
    odenen_tutar: float = 0.0
    tarih: str = ""

@dataclass
class Siparis:
    siparis_id: Optional[int] = None
    masa_id: int = 0
    musteri_id: Optional[int] = None
    urun_id: int = 0
    adet: int = 1
    tarih: Optional[datetime] = None
    durum: str = "Hazırlanıyor"
    notlar: str = ""
    
    def __post_init__(self):
        if self.adet < 1:
            raise ValueError("Adet 1'den küçük olamaz")