# urun_tab_pyside.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit,
                                 QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
                                 QMessageBox, QDialog, QFormLayout, QDoubleSpinBox, QComboBox, QCheckBox) # QCheckBox eklendi
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QDoubleValidator, QColor # QColor buraya eklendi

import os # Dosya yolu kontrolü için eklendi

# DatabaseManager main_app üzerinden erişilecek

# Adisyon sekmesindeki hızlı satış butonlarını güncellemek için AdisyonTabPyside import edilmeli
# Bu import burada gerekli çünkü _add_product ve _edit_product metotları AdisyonTabPyside referansını kullanıyor.
# Ancak dairesel import sorunu yaşamamak için bu import'u metot içinde yapabiliriz.
# from adisyon_tab_pyside import AdisyonTabPyside # Dairesel import'u önlemek için commentlendi


# --- PySide6 Özel Diyalog Sınıfları ---

# Ürün Ekle/Düzenle Diyaloğu
class ProductDialogPyside(QDialog):
     def __init__(self, parent=None, product_data=None, db_manager=None):
         super().__init__(parent)
         self.db_manager = db_manager
         self.product_data = product_data # None ise Yeni Ürün, dolu ise Düzenle
         self.product_id = product_data['urun_id'] if product_data else None

         if self.product_data:
              self.setWindowTitle("Ürün Düzenle")
         else:
              self.setWindowTitle("Yeni Ürün Ekle")

         self.setModal(True)

         layout = QFormLayout(self)

         self.entry_name = QLineEdit(self)
         # Fiyat için DoubleSpinBox
         self.spinbox_price = QDoubleSpinBox(self)
         self.spinbox_price.setMinimum(0.01)
         self.spinbox_price.setMaximum(999999.99)
         self.spinbox_price.setDecimals(2)
         self.spinbox_price.setSingleStep(0.5)
         self.spinbox_price.setSuffix(" TL")
         self.spinbox_price.setKeyboardTracking(False)


         self.cmb_category = QComboBox(self)

         # Aktif CheckBox'ı
         self.check_active = QCheckBox("Aktif", self)
         self.check_active.setChecked(True) # Varsayılan olarak aktif

         layout.addRow("Ürün Adı:", self.entry_name)
         layout.addRow("Fiyat:", self.spinbox_price)
         layout.addRow("Kategori:", self.cmb_category)
         layout.addRow("Durum:", self.check_active)

         # Butonlar
         button_box = QWidget(self)
         button_layout = QHBoxLayout(button_box)
         button_layout.setContentsMargins(0, 0, 0, 0)

         self.btn_save = QPushButton("Kaydet", self)
         self.btn_cancel = QPushButton("İptal", self)

         button_layout.addWidget(self.btn_save)
         button_layout.addWidget(self.btn_cancel)

         layout.addRow(button_box)

         # Buton bağlantıları
         self.btn_save.clicked.connect(self.accept)
         self.btn_cancel.clicked.connect(self.reject)

         # Verileri yükle (Eğer düzenleme modu ise)
         if self.product_data:
             self.entry_name.setText(self.product_data['adi'])
             self.spinbox_price.setValue(self.product_data['fiyat'])
             self.check_active.setChecked(bool(self.product_data['aktif'])) # 0 veya 1'i bool'a çevir

         # Kategori ComboBox'ını doldur (database manager üzerinden)
         self._load_categories()

     def _load_categories(self):
          """Kategori ComboBox'ını veritabanındaki kategorilerle doldurur."""
          if self.db_manager:
              categories = self.db_manager.get_all_categories()
              self.cmb_category.clear()
              # self.cmb_category.addItem("Kategori Seçin", None) # İlk boş öğe
              self.cmb_category.addItem("Kategori Seçin", -1) # Veritabanında category_id 0 veya None ise -1 kullanmak daha güvenli olabilir

              for cat in categories:
                   self.cmb_category.addItem(cat['adi'], cat['kategori_id'])

              # Eğer düzenleme modu ise, ürünün kategorisini seç
              if self.product_data and self.product_data['kategori_id'] is not None:
                  index = self.cmb_category.findData(self.product_data['kategori_id'])
                  if index != -1:
                       self.cmb_category.setCurrentIndex(index)
                  else:
                       # Ürünün kategorisi yoksa veya silinmişse varsayılanı seç
                       self.cmb_category.setCurrentIndex(0)
              else:
                  # Yeni ürün eklerken varsayılan olarak ilk boş öğeyi seç
                  self.cmb_category.setCurrentIndex(0)


     def get_product_data(self):
         """Diyalogdaki bilgileri dict olarak döndürür."""
         if not self.entry_name.text().strip():
              QMessageBox.warning(self, "Uyarı", "Ürün adı boş bırakılamaz.")
              return None

         # Kategori ID'yi al, eğer "-1" seçiliyse None olarak ayarla
         selected_category_data = self.cmb_category.currentData()
         kategori_id = selected_category_data if selected_category_data != -1 else None


         return {
             'urun_id': self.product_id,
             'adi': self.entry_name.text().strip(),
             'fiyat': self.spinbox_price.value(),
             'kategori_id': kategori_id, # None veya kategori_id
             'aktif': int(self.check_active.isChecked()) # True/False'u 1/0'a çevir
         }


# --- Ana Ürün Sekmesi Sınıfı ---

# urun_tab_pyside.py yükleniyor. Dosya yolu: ... (Debug satırı eklendi)
print(f"urun_tab_pyside.py yükleniyor. Dosya yolu: {os.path.abspath(__file__)}") # <<< Bu satır yukarıda olmalı


class UrunTabPyside(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app # Ana uygulama instance'ı
        self.db_manager = main_app.db_manager # DatabaseManager instance'ı

        self._create_ui()
        self._configure_styles() # Stilleri yapılandırma metodu eklendi

        # Sekme ilk açıldığında veya güncellenmesi gerektiğinde çağrılacak metot
        # load_data artık _on_tab_change tarafından çağrılıyor
        # self.load_data()

        # Buton bağlantıları
        self.btn_add_product.clicked.connect(self._add_product)
        self.btn_edit_product.clicked.connect(self._edit_product)
        self.btn_delete_product.clicked.connect(self._delete_product)
        self.entry_search.textChanged.connect(self.filter_products) # Filtreleme metodu bağlantısı
        self.cmb_kategori_filter.currentIndexChanged.connect(self.filter_products) # Filtreleme metodu bağlantısı


    def _create_ui(self):
        """Ürünler sekmesi arayüzünü oluşturur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Kontrol Butonları ve Arama/Filtre alanı için yatay layout
        controls_layout = QHBoxLayout()

        # Arama/Filtre alanı
        search_label = QLabel("Ara/Filtre:", self)
        self.entry_search = QLineEdit(self)
        self.entry_search.setPlaceholderText("Ürün adı ara...")

        # Kategori Filtre Combobox'ı
        filter_label = QLabel("Kategori:", self)
        self.cmb_kategori_filter = QComboBox(self)
        self.cmb_kategori_filter.setEditable(False)

        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.entry_search)
        controls_layout.addWidget(filter_label)
        controls_layout.addWidget(self.cmb_kategori_filter)
        controls_layout.addStretch() # Arama/Filtre alanını sola yaslar

        # Yeni, Düzenle, Sil butonları
        self.btn_add_product = QPushButton("Yeni Ürün", self)
        self.btn_edit_product = QPushButton("Düzenle", self)
        self.btn_delete_product = QPushButton("Sil", self)

        controls_layout.addWidget(self.btn_add_product)
        controls_layout.addWidget(self.btn_edit_product)
        controls_layout.addWidget(self.btn_delete_product)

        main_layout.addLayout(controls_layout) # Kontrol layout'unu ana layout'a ekle

        # Ürün listesi için TableWidget
        self.table_products = QTableWidget(self)
        self.table_products.setColumnCount(6) # urun_id, adi, fiyat, kategori_id, aktif, kategori_adi
        self.table_products.setHorizontalHeaderLabels(["ID", "Ürün Adı", "Fiyat", "Kategori ID", "Aktif", "Kategori"])
        self.table_products.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Ürün Adı sütununu genişlet
        self.table_products.setEditTriggers(QAbstractItemView.NoEditTriggers) # Tabloyu düzenlenemez yap
        self.table_products.setSelectionBehavior(QAbstractItemView.SelectRows) # Satır seçimi yap
        self.table_products.setSelectionMode(QAbstractItemView.SingleSelection) # Tekli seçim yap

        # ID, Kategori ID ve Aktif sütunlarını gizle (isteğe bağlı ama genellikle daha temiz durur)
        self.table_products.setColumnHidden(0, True) # ID sütunu
        self.table_products.setColumnHidden(3, True) # Kategori ID sütunu
        self.table_products.setColumnHidden(4, True) # Aktif sütunu

        main_layout.addWidget(self.table_products) # Tabloyu ana layout'a ekle

        # Placeholder etiketi kaldırıldı

    def _configure_styles(self):
        """Ürünler sekmesi için özel stilleri yapılandırır."""
        # Buraya daha sonra ürün sekmesine özel stiller eklenecek
        pass

    def load_data(self):
        """Ürünler sekmesi aktif olduğunda verileri yükler ve tabloyu doldurur."""
        print("Ürünler sekmesi verileri yükleniyor...") # <<< Bu print çalışmalı
        self.table_products.setRowCount(0) # Tabloyu temizle

        products = self.db_manager.get_all_products(include_inactive=True) # Pasif ürünleri de alalım

        if not products:
            print("Veritabanında ürün bulunamadı.")
            # Tablo zaten boş, placeholder gösterilebilir veya bilgilendirme eklenebilir
            # self.placeholder_label.setVisible(True) # Placeholder geri gösterilebilir
            return

        # self.placeholder_label.setVisible(False) # Placeholder gizlenir

        self.table_products.setRowCount(len(products)) # Tabloya ürün sayısı kadar satır ekle

        for row_index, product in enumerate(products):
            # Sütunlar: ID (Gizli), Ürün Adı, Fiyat, Kategori ID (Gizli), Aktif (Gizli), Kategori
            item_id = QTableWidgetItem(str(product['urun_id']))
            item_name = QTableWidgetItem(product['adi'])
            item_price = QTableWidgetItem(f"{product['fiyat']:.2f}") # Fiyat formatı
            item_category_id = QTableWidgetItem(str(product['kategori_id']))
            item_active = QTableWidgetItem(str(product['aktif']))

            # Kategori adını alalım (eğer kategori_id varsa)
            category_name = "Belirtilmemiş"
            if product['kategori_id'] is not None:
                 category = self.db_manager.get_category_by_id(product['kategori_id'])
                 if category:
                      category_name = category['adi']

            item_category_name = QTableWidgetItem(category_name)

            # Ürün pasif ise satırı gri yap
            if not product['aktif']:
                font = item_name.font()
                font.setItalic(True) # Pasif ürün adını italik yap
                item_name.setFont(font)
                color = QColor(Qt.gray)
                item_id.setForeground(color)
                item_name.setForeground(color)
                item_price.setForeground(color)
                item_category_id.setForeground(color)
                item_active.setForeground(color)
                item_category_name.setForeground(color)


            self.table_products.setItem(row_index, 0, item_id)
            self.table_products.setItem(row_index, 1, item_name)
            self.table_products.setItem(row_index, 2, item_price)
            self.table_products.setItem(row_index, 3, item_category_id)
            self.table_products.setItem(row_index, 4, item_active)
            self.table_products.setItem(row_index, 5, item_category_name)

        print(f"Ürünler tablosuna {len(products)} adet ürün yüklendi.") # <<< Bu print çalışmalı

        # Filtrelemeyi yükledikten sonra uygula (varsayılan tüm ürünler)
        # self.filter_products() # filter_products çağrısı load_data içinde olmamalı, sonsuz döngüye neden olabilir.

    def _add_product(self):
         """Yeni ürün ekleme diyaloğunu açar."""
         print("Yeni ürün ekle")
         dialog = ProductDialogPyside(self, db_manager=self.db_manager)
         if dialog.exec() == QDialog.Accepted:
             product_data = dialog.get_product_data()
             if product_data:
                 success = self.db_manager.add_product(product_data)
                 if success:
                     QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi.")
                     self.load_data() # Tabloyu yeniden yükle
                     # Adisyon sekmesindeki hızlı satış butonlarını da güncelle
                     # Dairesel import'u önlemek için burada import yapalım
                     try:
                         from adisyon_tab_pyside import AdisyonTabPyside
                         if hasattr(self.main_app, 'adisyon_tab') and isinstance(self.main_app.adisyon_tab, AdisyonTabPyside):
                             self.main_app.adisyon_tab.filter_hizli_satis_buttons()
                     except ImportError:
                         print("AdisyonTabPyside import edilemedi. Hızlı satış butonları güncellenemedi.")


    def _edit_product(self):
         """Seçili ürünü düzenleme diyaloğunu açar."""
         selected_items = self.table_products.selectedItems()
         if not selected_items:
             QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir ürün seçin.")
             return

         # Seçili satırın ID'sini al
         selected_row = selected_items[0].row()
         product_id = int(self.table_products.item(selected_row, 0).text())

         # Ürün verilerini veritabanından çek
         product_data = self.db_manager.get_product_by_id(product_id)

         if product_data:
              print(f"Ürün düzenle: ID {product_id}")
              dialog = ProductDialogPyside(self, product_data=product_data, db_manager=self.db_manager)
              if dialog.exec() == QDialog.Accepted:
                  updated_product_data = dialog.get_product_data()
                  if updated_product_data:
                      success = self.db_manager.update_product(updated_product_data)
                      if success:
                          QMessageBox.information(self, "Başarılı", "Ürün başarıyla güncellendi.")
                          self.load_data() # Tabloyu yeniden yükle
                          # Adisyon sekmesindeki hızlı satış butonlarını da güncelle
                          # Dairesel import'u önlemek için burada import yapalım
                          try:
                              from adisyon_tab_pyside import AdisyonTabPyside
                              if hasattr(self.main_app, 'adisyon_tab') and isinstance(self.main_app.adisyon_tab, AdisyonTabPyside):
                                  self.main_app.adisyon_tab.filter_hizli_satis_buttons()
                          except ImportError:
                              print("AdisyonTabPyside import edilemedi. Hızlı satış butonları güncellenemedi.")
         else:
             QMessageBox.critical(self, "Hata", "Seçili ürün bilgisi veritabanında bulunamadı.")


    def _delete_product(self):
         """Seçili ürünü siler."""
         selected_items = self.table_products.selectedItems()
         if not selected_items:
             QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ürün seçin.")
             return

         # Seçili satırın ID'sini ve adını al
         selected_row = selected_items[0].row()
         product_id = int(self.table_products.item(selected_row, 0).text())
         product_name = self.table_products.item(selected_row, 1).text()


         reply = QMessageBox.question(self, "Silme Onayı", f"'{product_name}' ürününü silmek istediğinizden emin misiniz?\nBu işlem geri alınamaz!",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

         if reply == QMessageBox.Yes:
             # Ürünün herhangi bir açık veya tamamlanmış adisyonda olup olmadığını kontrol et (İsteğe bağlı ama iyi bir kontrol)
             # Simplistik yaklaşım: Direkt silmeye çalış, FK hatası olursa kullanıcıyı bilgilendir
             try:
                 success = self.db_manager.delete_product(product_id)
                 if success:
                     QMessageBox.information(self, "Başarılı", "Ürün başarıyla silindi.")
                     self.load_data() # Tabloyu yeniden yükle
                     # Adisyon sekmesindeki hızlı satış butonlarını da güncelle
                     # Dairesel import'u önlemek için burada import yapalım
                     try:
                         from adisyon_tab_pyside import AdisyonTabPyside
                         if hasattr(self.main_app, 'adisyon_tab') and isinstance(self.main_app.adisyon_tab, AdisyonTabPyside):
                             self.main_app.adisyon_tab.filter_hizli_satis_buttons()
                     except ImportError:
                         print("AdisyonTabPyside import edilemedi. Hızlı satış butonları güncellenemedi.")


             except Exception as e:
                 # FK hatası veya başka bir veritabanı hatası olabilir
                 QMessageBox.critical(self, "Hata", f"Ürün silinirken bir hata oluştu. Ürün adisyonlarda kullanılıyor olabilir.\nHata: {e}")


    def filter_products(self):
         """Arama kutusu ve kategori seçimine göre ürün tablosunu filtreler."""
         search_term = self.entry_search.text().strip().lower()
         selected_category_id = self.cmb_kategori_filter.currentData() # None veya kategori_id

         for row in range(self.table_products.rowCount()):
             # Ürün Adı sütunu (Index 1)
             item_name = self.table_products.item(row, 1)
             # Kategori ID sütunu (Index 3)
             item_category_id = self.table_products.item(row, 3)

             name_match = (search_term in item_name.text().lower())

             # item_category_id'nin None olup olmadığını kontrol et
             category_id = int(item_category_id.text()) if item_category_id and item_category_id.text() else None
             # Eğer kategori ID -1 (Kategori Seçin) ise None olarak kabul et
             if category_id == -1:
                  category_id = None

             category_match = (selected_category_id is None or selected_category_id == category_id)

             # Hem isim hem de kategori filtresine uyuyorsa satırı göster, yoksa gizle
             if name_match and category_match:
                 self.table_products.setRowHidden(row, False)
             else:
                 self.table_products.setRowHidden(row, True)

    def load_categories_combobox(self):
        """Kategori filtre Combobox'ını günceller (Adisyon sekmesindeki metodun benzeri)."""
        print("Ürünler sekmesi kategori combobox yükleniyor...")
        categories = self.db_manager.get_all_categories()

        self.cmb_kategori_filter.clear()
        self.cmb_kategori_filter.addItem("Tümü", None) # Varsayılan olarak Tümü, data None

        for cat in categories:
             self.cmb_kategori_filter.addItem(cat['adi'], cat['kategori_id'])

        self.cmb_kategori_filter.setCurrentIndex(0) # Varsayılan olarak Tümü seçili


# Adisyon sekmesindeki hızlı satış butonlarını güncellemek için AdisyonTabPyside import edilmeli
# from adisyon_tab_pyside import AdisyonTabPyside # Dairesel import'u önlemek için metod içinde yapılıyor