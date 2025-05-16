# masa_tab_pyside.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, # <<< BURASI: QHBoxLayout import edildi
                                 QGridLayout, QLabel, QMessageBox, QSizePolicy, QDialog,
                                 QInputDialog) # QInputDialog manuel yıl girişi için kullanılabilir
from PySide6.QtCore import Qt, QTimer, QDateTime, QSize
from PySide6.QtGui import QColor, QPalette

import constants
from datetime import datetime, timedelta

# Özel Masa Silme Onay Diyaloğu (İstenirse daha gelişmiş yapılabilir)
class MasaDeleteConfirmDialog(QDialog):
    def __init__(self, parent, masa_no):
        super().__init__(parent)
        self.setWindowTitle("Masa Silme Onayı")
        self.setModal(True) # Modal olarak aç

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Masa {masa_no} silmek istediğinizden emin misiniz?"))
        layout.addWidget(QLabel("Bu işlem geri alınamaz!", styleSheet="color: red;"))

        button_box = QWidget()
        button_layout = QHBoxLayout(button_box)
        btn_yes = QPushButton("Evet")
        btn_no = QPushButton("Hayır")
        button_layout.addWidget(btn_yes)
        button_layout.addWidget(btn_no)
        layout.addWidget(button_box)

        btn_yes.clicked.connect(self.accept) # Evet'e basınca QDialog'u accept ile kapat
        btn_no.clicked.connect(self.reject)   # Hayır'a basınca QDialog'u reject ile kapat

class MasaTabPyside(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app # main_pyside.py'deki ana uygulama objesi

        self.masa_buttons = {} # Masa numaralarına karşılık gelen buton objeleri
        self.delete_mode = False # Masa silme modu aktif mi?

        self._create_ui()
        self._configure_styles() # PySide6 stilleri

        # Geçikmiş masa kontrolü için QTimer
        self.late_table_timer = QTimer(self)
        self.late_table_timer.timeout.connect(self.check_late_tables)
        # Timer başlangıçta başlatılmayacak, sekme değiştiğinde başlatılacak.


    def _create_ui(self):
        """Masalar sekmesi arayüzünü oluşturur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10) # Kenar boşlukları

        # Butonların yerleşeceği ızgara layout
        self.masa_grid_layout = QGridLayout()
        self.masa_grid_layout.setSpacing(10) # Butonlar arası boşluk

        # Masa butonlarını buraya dinamik olarak ekleyeceğiz.
        # Load masa buttons metodu çağrıldığında bu layout doldurulacak.

        main_layout.addLayout(self.masa_grid_layout)

        # Alt kontrol alanı (Masa Ekle/Sil)
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget) # <<< BURASI: QHBoxLayout kullanılıyor
        control_layout.setContentsMargins(0, 0, 0, 0) # Kenar boşlukları

        self.lbl_status = QLabel("Hazır.")
        control_layout.addWidget(self.lbl_status)

        control_layout.addStretch() # Etiket ile butonlar arasına boşluk koy

        self.btn_add_masa = QPushButton("Masa Ekle")
        self.btn_add_masa.clicked.connect(self._add_masa)
        control_layout.addWidget(self.btn_add_masa)

        self.btn_delete_masa = QPushButton("Masa Sil")
        self.btn_delete_masa.clicked.connect(self._toggle_delete_mode)
        control_layout.addWidget(self.btn_delete_masa)

        main_layout.addWidget(control_widget)


    def _configure_styles(self):
        """PySide6 widget stillerini yapılandırır."""
        # Genel buton stilini tanımla (varsayılan)
        self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border: 1px solid #8f8f91;
                border-radius: 5px;
                background-color: #f0f0f0;
                color: black;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
            QPushButton#MasaBoş {
                 background-color: #d4edda; /* Açık yeşil */
                 color: #040404; /* Koyu yeşil */
            }
            QPushButton#MasaBoş:hover {
                 background-color: #c3e6cb;
            }
            QPushButton#MasaDolu {
                 background-color: #f8d7da; /* Açık kırmızı */
                 color: #721c24; /* Koyu kırmızı */
            }
            QPushButton#MasaDolu:hover {
                 background-color: #f5c6cb;
            }
            QPushButton#MasaOdemeBekliyor {
                 background-color: #fff3cd; /* Açık sarı */
                 color: #856404; /* Koyu sarı */
            }
             QPushButton#MasaOdemeBekliyor:hover {
                 background-color: #ffeeba;
            }
            QPushButton#MasaGecikmiş {
                 background-color: #dc3545; /* Kırmızı */
                 color: white; /* Beyaz */
            }
            QPushButton#MasaGecikmiş:hover {
                 background-color: #c82333;
            }
            QPushButton#MasaSilMode {
                 background-color: #ffcccc; /* Açık pembe */
                 color: #cc0000; /* Koyu kırmızı */
                 font-weight: bold;
                 border-color: #cc0000;
            }
            QPushButton#MasaSilMode:hover {
                 background-color: #ffaaaa;
            }
            QPushButton[selected="true"] { /* Seçili masa için stil */
                 border: 3px solid yellow; /* Seçili masa için sarı kenarlık */
            }
        """)


    def load_masa_buttons(self):
        """Veritabanından masa bilgilerini çeker ve butonları oluşturur/günceller."""
        print("Masa butonları yükleniyor...") # Debug

        # Mevcut butonları temizle
        for i in reversed(range(self.masa_grid_layout.count())):
            # layout'tan öğeyi al
            item = self.masa_grid_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    # Widget'ı layout'tan kaldır
                    self.masa_grid_layout.removeWidget(widget)
                    # Widget'ı sil
                    widget.deleteLater() # Widget'ı silmek için güvenli yol


        self.masa_buttons = {} # Sözlüğü temizle

        masalar = self.main_app.db_manager.get_all_masalar()

        row, col = 0, 0
        max_cols = 5 # Izgaradaki maksimum sütun sayısı

        for masa in masalar:
            masa_no = masa['masa_no']
            durum = masa['durum']
            toplam = masa['guncel_toplam']
            musteri_adi = masa['musteri_adi']

            # Buton metni ve durumu belirle
            button_text = f"Masa {masa_no}\nDurum: {durum}"
            if musteri_adi:
                 button_text += f"\nMüşteri: {musteri_adi}"

            # Toplam bilgisi dolu masalar için
            if durum != 'Boş' and toplam is not None and toplam >= 0: # Toplam 0 veya negatifse de gösterilebilir
                button_text += f"\nToplam: {toplam:.2f} TL"


            btn = QPushButton(button_text)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Otomatik boyutlandırma
            btn.setMinimumSize(100, 80) # Minimum boyut ayarlayabilirsiniz

            # Stili durumuna göre ayarla (Object Name kullanarak CSS stilinde belirttik)
            if durum == 'Boş':
                btn.setObjectName("MasaBoş")
            elif durum == 'Dolu':
                btn.setObjectName("MasaDolu")
            elif durum == 'Ödeme Bekliyor':
                 btn.setObjectName("MasaOdemeBekliyor")
            elif durum == 'Geçikmiş': # Yeni Geçikmiş durumu
                 btn.setObjectName("MasaGecikmiş")
            else:
                 btn.setObjectName("MasaVarsayilan") # Tanımsız durumlar için

            # Butona masa numarasını sakla (lambda ile bağlantı için)
            btn.setProperty("masa_no", masa_no)

            # Buton tıklama olayını bağla
            btn.clicked.connect(lambda checked, mn=masa_no: self._on_masa_button_clicked(mn))

            self.masa_grid_layout.addWidget(btn, row, col)
            self.masa_buttons[masa_no] = btn # Buton referansını sakla

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Izgara sütunlarını eşit genişlikte yap
        for i in range(max_cols):
            self.masa_grid_layout.setColumnStretch(i, 1)

        # PySide6'da row stretch genellikle içeriğe göre otomatik ayarlanır,
        # ancak isterseniz satırları da genişletmek için setRowStretch kullanabilirsiniz.
        # for i in range(row + 1):
        #     self.masa_grid_layout.setRowStretch(i, 1)

        self.updateGeometry() # Layout güncellendiğinde pencere boyutunu yeniden hesapla


    def _on_masa_button_clicked(self, masa_no):
        """Masa butonuna tıklandığında çağrılır."""
        if self.delete_mode:
            # Silme modu aktifse masayı silmeye çalış
            self._delete_masa(masa_no)
        else:
            # Normal modda masayı seç
            self.select_masa(masa_no)


    def select_masa(self, masa_no):
        """Belirli bir masayı seçer ve Adisyon sekmesine geçer."""
        # Seçili masa stilini güncelle
        self._update_selected_masa_style(masa_no)

        # Ana uygulamadaki aktif masa bilgisini güncelle
        self.main_app.aktif_masa = masa_no

        # Seçilen masanın aktif siparişi var mı kontrol et
        masa_info = self.main_app.db_manager.get_masa_info(self.main_app.aktif_masa)

        if masa_info and masa_info['aktif_siparis_id']:
             self.main_app.aktif_siparis_id = masa_info['aktif_siparis_id']
             print(f"Aktif Masa Ayarlandı: Masa {self.main_app.aktif_masa}, Aktif Sipariş ID: {self.main_app.aktif_siparis_id}")
        else:
             self.main_app.aktif_siparis_id = None
             print(f"Aktif Masa Ayarlandı: Masa {self.main_app.aktif_masa}, Aktif Sipariş Yok.")

        # Adisyon sekmesine geç (index 1)
        self.main_app.tab_widget.setCurrentIndex(1)


    def _update_selected_masa_style(self, selected_masa_no):
        """Seçili masa butonunun stilini günceller, diğerlerinin stilini sıfırlar."""
        for masa_no, btn in self.masa_buttons.items():
            if masa_no == selected_masa_no:
                # Seçili masaya özel stil ekle
                btn.setProperty("selected", True)
                btn.style().polish(btn) # Stili uygula
            else:
                # Diğer masaların stilini sıfırla
                btn.setProperty("selected", False)
                btn.style().polish(btn) # Stili uygula


    def _add_masa(self):
        """Yeni bir masa ekler."""
        # Eğer silme modundaysak, masa ekleme işlemini yapma
        if self.delete_mode:
            QMessageBox.warning(self, "Uyarı", "Masa silme modu aktif. Lütfen önce modu kapatın veya bir masa seçin.")
            return

        next_masa_no = self.main_app.db_manager.add_masa()

        if next_masa_no:
            QMessageBox.information(self, "Başarılı", f"Masa {next_masa_no} başarıyla eklendi.")
            self.load_masa_buttons() # Masa listesini ve butonları yeniden yükle


    def _toggle_delete_mode(self):
        """Masa silme modunu açar/kapatır."""
        self.delete_mode = not self.delete_mode
        self.update_delete_button_text() # Buton metnini ve görünümünü güncelle

        if self.delete_mode:
            QMessageBox.information(self, "Bilgi", "Silmek istediğiniz masaya tıklayın.")
            # Silme modu açıldığında seçili masa stilini sıfırla
            self._update_selected_masa_style(None) # None göndererek tüm seçimleri kaldır
            self.main_app.aktif_masa = None # Aktif masayı da sıfırla
            self.main_app.aktif_siparis_id = None # Aktif siparişi de sıfırla

        else:
            QMessageBox.information(self, "Bilgi", "Masa silme modu kapatıldı.")
            # Silme modu kapatıldığında seçili masa stilini sıfırla (yukarıda yapılıyor)


    def update_delete_button_text(self):
        """Masa Sil butonunun metnini ve stilini günceller."""
        if self.delete_mode:
            self.btn_delete_masa.setText("Modu Kapat")
            self.btn_delete_masa.setObjectName("MasaSilMode") # Silme modu stili
        else:
            self.btn_delete_masa.setText("Masa Sil")
            self.btn_delete_masa.setObjectName("") # Normal stil
        self.btn_delete_masa.style().polish(self.btn_delete_masa) # Stili uygula


    def _delete_masa(self, masa_no):
        """Belirli bir masayı siler (silme modu aktifken)."""
        # Masa silme modunu kapat
        self._toggle_delete_mode() # Modu kapat, butonu sıfırla


        if masa_no is None:
            QMessageBox.warning(self, "Uyarı", "Silinecek masa belirlenemedi.")
            return

        # Seçili masanın durumunu kontrol et (sadece boş masalar silinebilir)
        masa_info = self.main_app.db_manager.get_masa_info(masa_no)
        if masa_info and masa_info['durum'] != 'Boş':
            QMessageBox.warning(self, "Uyarı", f"Sadece boş masalar sililebilir. Masa {masa_no} durumu: {masa_info['durum']}")
            return

        # Kullanıcıdan silme onayı al (Özel diyalog kullanıldı)
        dialog = MasaDeleteConfirmDialog(self, masa_no)
        result = dialog.exec() # Diyalog modal olarak açılır ve kapanmasını bekler (accept=1, reject=0)


        if result == QDialog.Accepted: # Eğer kullanıcı 'Evet'e bastıysa
            success, message = self.main_app.db_manager.delete_masa(masa_no)

            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_masa_buttons() # Masa listesini ve butonları yeniden yükle

                # Eğer silinen masa aktif masa ise, aktif masa bilgisini sıfırla (Zaten _toggle_delete_mode içinde yapılıyor)
                # if self.main_app.aktif_masa == masa_no:
                #     self.main_app.aktif_masa = None
                #     self.main_app.aktif_siparis_id = None
                    # Adisyon sekmesi UI'ını güncellemek gerekebilir (main_pyside.py'deki _on_tab_change içinde halledilebilir veya doğrudan çağrılabilir)

            else:
                 QMessageBox.warning(self, "Uyarı", message) # delete_masa metotundan gelen uyarı mesajı

        else:
            QMessageBox.information(self, "Bilgi", "Silme işlemi iptal edildi.")


    def check_late_tables(self):
        """Geçikmiş masa kontrolünü yapar ve masa durumlarını günceller."""
        # Bu fonksiyon artık MasaTab'a taşındı
        late_tables_info = self.main_app.db_manager.get_late_table_info()
        now = datetime.now()

        for masa_info in late_tables_info:
            masa_no = masa_info['masa_no']
            son_islem_zamani_str = masa_info['son_islem_zamani']
            current_durum = masa_info['durum'] # Mevcut durumu al

            if son_islem_zamani_str:
                 son_islem_zamani = datetime.strptime(son_islem_zamani_str, "%Y-%m-%d %H:%M:%S")
                 # Eğer son işlem zamanı belirli bir eşikten eskiyse VE durumu zaten 'Geçikmiş' değilse
                 if now - son_islem_zamani > timedelta(minutes=constants.LATE_TABLE_THRESHOLD_MINUTES) and current_durum != 'Geçikmiş':
                     print(f"Masa {masa_no} geçikmiş olarak işaretleniyor.") # Debug
                     self.main_app.db_manager.update_masa_status(masa_no, 'Geçikmiş')
                     # Masa durumunu güncelledikten sonra butonları yeniden yükle
                     self.load_masa_buttons()
                 # Eğer masa daha önce geçikmiş olarak işaretlenmişse ve artık eşikten yeni durumdaysa
                 # (Bu durumda normalde durumu 'Dolu'ya döner ama bu akış henüz net tanımlanmadı)
                 # Şimdilik sadece geçikmiş işaretleme mantığı yeterli.


    def start_late_table_check(self):
        """Geçikmiş masa kontrol timer'ını başlatır."""
        # Timer'ı başlatmadan önce aktif olup olmadığını kontrol et
        if not self.late_table_timer.isActive():
             print("Geçikmiş masa kontrolü başlatıldı.") # Debug
             self.late_table_timer.start(constants.LATE_TABLE_CHECK_INTERVAL_MS)

    def stop_late_table_check(self):
        """Geçikmiş masa kontrol timer'ını durdurur."""
        if self.late_table_timer.isActive():
             print("Geçikmiş masa kontrolü durduruldu.") # Debug
             self.late_table_timer.stop()