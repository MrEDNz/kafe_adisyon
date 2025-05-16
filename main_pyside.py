# main_pyside.py

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget,
                                 QMessageBox, QLabel)
from PySide6.QtCore import Qt, QSize, QTimer
from datetime import datetime, date, timedelta

# Veritabanı yöneticisi ve sabitler
from database import DatabaseManager
import constants

# PySide6 tab sınıflarını import et
from masa_tab_pyside import MasaTabPyside
from adisyon_tab_pyside import AdisyonTabPyside # <<< Adisyon sekmesi import edildi
# Diğer sekmeler tamamlandığında importları buraya eklenecek
from urun_tab_pyside import UrunTabPyside
# from musteriler_tab_pyside import MusterilerTabPyside
# from raporlar_tab_pyside import RaporlarTabPyside

# Geçici olarak boş QWidget sınıfları tanımlayalım (henüz tamamlanmayan sekmeler için)

class MusterilerTabPyside(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent) # <<< Düzeltme: self yerine parent geçirildi
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Müşteriler Sekmesi (PySide6) - Yapım Aşamasında"))

class RaporlarTabPyside(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent) # <<< Düzeltme: self yerine parent geçirildi
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Raporlar Sekmesi (PySide6) - Yapım Aşamasında"))

class CafeAdisyonAppPyside(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Late Adisyon Programs (PySide6)")
        self.setGeometry(100, 100, 1200, 800)

        self.db_manager = DatabaseManager(constants.DB_NAME)

        self.aktif_masa = None
        self.aktif_siparis_id = None

        self.closeEvent = self._on_closing

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.masa_tab = MasaTabPyside(self)
        self.adisyon_tab = AdisyonTabPyside(self)
        self.urun_tab = UrunTabPyside(self)
        self.musteriler_tab = MusterilerTabPyside(self)
        self.raporlar_tab = RaporlarTabPyside(self)

        self.tab_widget.addTab(self.masa_tab, "Masalar")
        self.tab_widget.addTab(self.adisyon_tab, "Adisyon")
        self.tab_widget.addTab(self.urun_tab, "Ürünler")
        self.tab_widget.addTab(self.musteriler_tab, "Müşteriler")
        self.tab_widget.addTab(self.raporlar_tab, "Raporlar")

        self.tab_widget.currentChanged.connect(self._on_tab_change)

        self.tab_widget.setCurrentIndex(0)

        # Otomatik arşivleme kontrolü şimdilik yorum satırı
        # self._check_and_perform_auto_archive()


    # Otomatik arşivleme kontrolü (yorum satırı)
    def _check_and_perform_auto_archive(self):
        """Uygulama başlangıcında otomatik arşivleme yapılması gerekip gerekmediğini kontrol eder (PySide6 versiyonu)."""
        # date modülünün import edildiğinden emin olun (from datetime import date)

        # today = date.today()
        # current_year = today.year
        # last_completed_year = current_year - 1 # Arşivlenecek yıl (geçen yıl)

        # last_archived_year_str = self.db_manager.get_setting("last_archived_year")

        # try:
        #     last_archived_year = int(last_archived_year_str) if last_archived_year_str else 0
        # except ValueError:
        #     last_archived_year = 0

        # if last_completed_year > last_archived_year:

        #      reply = QMessageBox.question(self, "Otomatik Arşivleme",
        #                                 f"'{last_completed_year}' yılına (dahil) ait tamamlanmış siparişler otomatik olarak arşivlensin ve ana veritabanından silinsin mi?\nBu işlem geri alınamaz!",
        #                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        #      if reply == QMessageBox.Yes:
        #          success, message = self.db_manager.archive_and_delete_old_orders(last_completed_year)

        #          if success:
        #               QMessageBox.information(self, "Arşivleme Başarılı", message)
        #               if hasattr(self, 'masa_tab') and isinstance(self.masa_tab, MasaTabPyside):
        #                   self.masa_tab.load_masa_buttons()

        #          else:
        #               QMessageBox.warning(self, "Arşivleme Hatası", message)
        #      else:
        #           QMessageBox.information(self, "Arşivleme İptal", "Otomatik arşivleme işlemi kullanıcı tarafından iptal edildi.")


    def _on_tab_change(self, index):
        """Sekme değiştiğinde ilgili sekmenin içeriğini yükler/günceller."""
        print(f"_on_tab_change metodu çağrıldı. Sekme indeksi: {index}, Sekme Adı: {self.tab_widget.tabText(index)}")

        # Sekme değiştiğinde geçikmiş masa kontrol timer'ını durdur (Masa sekmesi tamamlandıysa)
        if hasattr(self, 'masa_tab') and isinstance(self.masa_tab, MasaTabPyside):
             print("Masa tab timer durduruluyor.")
             self.masa_tab.stop_late_table_check()

        # İlgili sekmenin yükleme metotlarını çağır
        if index == 0: # Masalar sekmesi
             print("Masalar sekmesi seçildi.")
             if hasattr(self, 'masa_tab') and isinstance(self.masa_tab, MasaTabPyside):
                 print("MasaTabPyside instance bulundu, load_masa_buttons çağrılıyor.")
                 self.masa_tab.load_masa_buttons()
                 self.masa_tab.start_late_table_check() # Masa sekmesine dönüldüğünde timer'ı başlat
             else:
                  print("Hata: MasaTabPyside instance bulunamadı veya doğru tipte değil.")
        elif index == 1: # Adisyon sekmesi
            print("Adisyon sekmesi seçildi.")
            if hasattr(self, 'adisyon_tab') and isinstance(self.adisyon_tab, AdisyonTabPyside):
               print("AdisyonTabPyside instance bulundu, load_data çağrılıyor.")
               # <<< BURAYA YENİ PRİNT SATIRINI EKLEYİN
               print(f"Yüklenen adisyon_tab_pyside dosya yolu: {self.adisyon_tab.__class__.__module__}") # Modül adını yazdır
               import inspect
               try:
                   file_path = inspect.getfile(self.adisyon_tab.__class__)
                   print(f"Yüklenen adisyon_tab_pyside dosya yolu (inspect): {file_path}") # Dosya yolunu yazdırmaya çalış
               except TypeError:
                   print("inspect.getfile() AdisyonTabPyside için dosya yolu bulamadı.")

               self.adisyon_tab.load_data() # <<< Hata veren satır
            else:
                 print("Hata: AdisyonTabPyside instance bulunamadı veya doğru tipte değil.")
        elif index == 2: # Ürünler sekmesi
            print("Ürünler sekmesi seçildi.")
            if hasattr(self, 'urun_tab') and isinstance(self.urun_tab, UrunTabPyside):
                print("UrunTabPyside instance bulundu, load_data çağrılıyor.")
                # self.urun_tab.load_data() # Bu sekme henüz tamamlanmadı
            else:
                 print("Hata: UrunTabPyside instance bulunamadı veya doğru tipte değil.")
                 
        # elif index == 3: # Müşteriler sekmesi
        # ...
        # elif index == 4: # Raporlar sekmesi
        # ...


    def _on_closing(self, event):
        """Pencere kapatılırken veritabanı bağlantısını kapatır."""
        reply = QMessageBox.question(self, 'Çıkış', 'Uygulamadan çıkmak istediğinizden emin misiniz?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Uygulama kapatılırken MasaTab'ın timer'ını durdurmak önemli (Masa sekmesi tamamlandıysa)
            if hasattr(self, 'masa_tab') and isinstance(self.masa_tab, MasaTabPyside):
                 self.masa_tab.stop_late_table_check()

            if self.db_manager:
                self.db_manager.close()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CafeAdisyonAppPyside()
    # Otomatik arşivleme kontrolü şimdilik yorum satırı
    # window._check_and_perform_auto_archive()
    window.show()
    sys.exit(app.exec())