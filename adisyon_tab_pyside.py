# adisyon_tab_pyside.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                 QLineEdit, QPushButton, QComboBox, QTreeWidget,
                                 QTreeWidgetItem, QMessageBox, QSizePolicy,
                                 QScrollArea, QGridLayout, QDialog, QDoubleSpinBox,
                                 QHeaderView)
from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtGui import QColor, QPalette, QDoubleValidator

import constants
from datetime import datetime, timedelta
from masa_tab_pyside import MasaTabPyside

import os # <<< Yeni import
print(f"adisyon_tab_pyside.py yükleniyor. Dosya yolu: {os.path.abspath(__file__)}") # <<< Yeni debug satırı

# PySide6 Özel Diyalog Sınıfları
class DiscountDialogPyside(QDialog):
    def __init__(self, parent, current_brut_total):
        super().__init__(parent)
        self.setWindowTitle("İskonto Uygula")
        self.setModal(True)
        self.parent = parent

        self.discount_amount = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Uygulanacak iskonto miktarını girin:", self))
        layout.addWidget(QLabel(f"Brüt Toplam: {current_brut_total:.2f} TL", self, styleSheet="font-weight: bold;"))

        self.spinbox_discount = QDoubleSpinBox(self)
        self.spinbox_discount.setMinimum(0.0)
        self.spinbox_discount.setMaximum(current_brut_total)
        self.spinbox_discount.setDecimals(2)
        self.spinbox_discount.setSingleStep(0.5)
        self.spinbox_discount.setSuffix(" TL")
        self.spinbox_discount.setKeyboardTracking(False)
        layout.addWidget(self.spinbox_discount)

        button_box = QWidget(self)
        button_layout = QHBoxLayout(button_box)
        button_layout.setContentsMargins(0, 0, 0, 0)

        btn_apply = QPushButton("Uygula", self)
        btn_cancel = QPushButton("İptal", self)

        button_layout.addWidget(btn_apply)
        button_layout.addWidget(btn_cancel)

        layout.addWidget(button_box)

        btn_apply.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        self.spinbox_discount.returnPressed.connect(self.accept)


    def accept(self):
        self.discount_amount = self.spinbox_discount.value()
        super().accept()

    def reject(self):
        self.discount_amount = None
        super().reject()

    def get_discount_amount(self):
        return self.discount_amount

class PartialPaymentDialogPyside(QDialog):
    def __init__(self, parent, remaining_balance):
        super().__init__(parent)
        self.setWindowTitle("Parçalı Ödeme Al")
        self.setModal(True)
        self.parent = parent

        self.payment_amount = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Alınacak parçalı ödeme miktarını girin:", self))
        layout.addWidget(QLabel(f"Kalan Tutar: {remaining_balance:.2f} TL", self, styleSheet="font-weight: bold;"))

        self.spinbox_payment = QDoubleSpinBox(self)
        self.spinbox_payment.setMinimum(0.01)
        self.spinbox_payment.setMaximum(max(remaining_balance, 0.01))
        self.spinbox_payment.setDecimals(2)
        self.spinbox_payment.setSingleStep(0.5)
        self.spinbox_payment.setSuffix(" TL")
        self.spinbox_payment.setKeyboardTracking(False)
        self.spinbox_payment.setValue(remaining_balance)
        layout.addWidget(self.spinbox_payment)

        button_box = QWidget(self)
        button_layout = QHBoxLayout(button_box)
        button_layout.setContentsMargins(0, 0, 0, 0)

        btn_apply = QPushButton("Ödeme Al", self)
        btn_cancel = QPushButton("İptal", self)

        button_layout.addWidget(btn_apply)
        button_layout.addWidget(btn_cancel)

        layout.addWidget(button_box)

        btn_apply.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        self.spinbox_payment.returnPressed.connect(self.accept)


    def accept(self):
        self.payment_amount = self.spinbox_payment.value()
        if self.payment_amount <= 0:
             QMessageBox.warning(self, "Uyarı", "Ödeme miktarı pozitif bir sayı olmalıdır.")
             return
        super().accept()

    def reject(self):
        self.payment_amount = None
        super().reject()

    def get_payment_amount(self):
        return self.payment_amount

class AdisyonTabPyside(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        self._customer_list_data = []

        self._create_ui()
        self._configure_styles()

    def _create_ui(self):
        """Adisyon sekmesi arayüzünü oluşturur."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        top_info_widget = QWidget(self)
        top_info_layout = QHBoxLayout(top_info_widget)
        top_info_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_aktif_masa = QLabel("Aktif Masa: Seçilmedi", self)
        self.lbl_aktif_masa.setStyleSheet("font-weight: bold; font-size: 12pt;")
        top_info_layout.addWidget(self.lbl_aktif_masa)

        customer_assign_groupbox = QWidget(self)
        customer_assign_layout = QHBoxLayout(customer_assign_groupbox)

        customer_assign_layout.addWidget(QLabel("Müşteri Ata:", self))
        self.cmb_musteri_sec = QComboBox(self)
        self.cmb_musteri_sec.setFixedWidth(200)
        self.cmb_musteri_sec.setEditable(False)
        customer_assign_layout.addWidget(self.cmb_musteri_sec)

        self.btn_atama_yap = QPushButton("Ata", self)
        self.btn_atama_yap.clicked.connect(self._assign_customer_to_order)
        customer_assign_layout.addWidget(self.btn_atama_yap)

        self.lbl_atanan_musteri = QLabel("Atanan: Yok", self)
        customer_assign_layout.addWidget(self.lbl_atanan_musteri)

        top_info_layout.addWidget(customer_assign_groupbox)
        top_info_layout.addStretch()

        search_filter_widget = QWidget(self)
        search_filter_layout = QHBoxLayout(search_filter_widget)
        search_filter_layout.setContentsMargins(0, 0, 0, 0)

        search_filter_layout.addWidget(QLabel("Ara/Filtre:", self))
        self.entry_search = QLineEdit(self)
        self.entry_search.setPlaceholderText("Ürün adı ara...")
        self.entry_search.textChanged.connect(self.filter_hizli_satis_buttons)
        search_filter_layout.addWidget(self.entry_search)

        self.cmb_kategori_filter = QComboBox(self)
        self.cmb_kategori_filter.setEditable(False)
        self.cmb_kategori_filter.currentIndexChanged.connect(self.filter_hizli_satis_buttons)
        search_filter_layout.addWidget(self.cmb_kategori_filter)

        top_info_layout.addWidget(search_filter_widget)

        main_layout.addWidget(top_info_widget)

        hizli_satis_label = QLabel("Hızlı Satış Ürünleri:", self)
        main_layout.addWidget(hizli_satis_label)

        self.hizli_satis_scroll_area = QScrollArea(self)
        self.hizli_satis_scroll_area.setWidgetResizable(True)
        self.hizli_satis_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.hizli_satis_button_widget = QWidget()
        self.hizli_satis_grid_layout = QGridLayout(self.hizli_satis_button_widget)
        self.hizli_satis_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.hizli_satis_grid_layout.setSpacing(5)

        self.hizli_satis_scroll_area.setWidget(self.hizli_satis_button_widget)
        main_layout.addWidget(self.hizli_satis_scroll_area, 2)

        cart_label = QLabel("Adisyon Sepeti:", self)
        main_layout.addWidget(cart_label)

        self.cart_treeview = QTreeWidget(self)
        self.cart_treeview.setHeaderLabels(["Ürün Adı", "Miktar", "Birim Fiyat", "Tutar", "Eklenme Saat", "detay_id"])
        self.cart_treeview.setColumnHidden(5, True)

        header = self.cart_treeview.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.resizeSection(1, 70)
        header.resizeSection(2, 90)
        header.resizeSection(3, 90)
        header.resizeSection(4, 90)
        header.resizeSection(5, 0)

        self.cart_treeview.setSortingEnabled(False)
        self.cart_treeview.setSelectionBehavior(QTreeWidget.SelectRows)
        self.cart_treeview.setItemsExpandable(False)
        self.cart_treeview.setRootIsDecorated(False)

        main_layout.addWidget(self.cart_treeview, 3)

        bottom_controls_widget = QWidget(self)
        bottom_controls_layout = QHBoxLayout(bottom_controls_widget)
        bottom_controls_layout.setContentsMargins(0, 0, 0, 0)

        quantity_widget = QWidget(self)
        quantity_layout = QHBoxLayout(quantity_widget)
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        quantity_layout.addWidget(QLabel("Miktar:", self))
        self.entry_quantity = QLineEdit(self)
        self.entry_quantity.setFixedWidth(50)
        self.entry_quantity.setText("1")
        self.entry_quantity.setValidator(QDoubleValidator(0.01, 9999.99, 2, self))
        quantity_layout.addWidget(self.entry_quantity)

        bottom_controls_layout.addWidget(quantity_widget)
        bottom_controls_layout.addSpacing(10)

        self.btn_remove_selected = QPushButton("Seçiliyi Sil", self)
        self.btn_remove_selected.clicked.connect(self.remove_selected_cart_item)
        bottom_controls_layout.addWidget(self.btn_remove_selected)

        self.btn_clear_cart = QPushButton("Sepeti Temizle", self)
        self.btn_clear_cart.clicked.connect(self.clear_cart)
        bottom_controls_layout.addWidget(self.btn_clear_cart)

        self.btn_apply_discount = QPushButton("İskonto Uygula", self)
        self.btn_apply_discount.clicked.connect(self.apply_discount)
        bottom_controls_layout.addWidget(self.btn_apply_discount)

        bottom_controls_layout.addStretch()

        totals_payments_widget = QWidget(self)
        totals_payments_layout = QVBoxLayout(totals_payments_widget)
        totals_payments_layout.setContentsMargins(0, 0, 0, 0)
        totals_payments_layout.setSpacing(5)

        self.lbl_brut_total = QLabel("Brüt Toplam: 0.00 TL", self)
        self.lbl_brut_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        totals_payments_layout.addWidget(self.lbl_brut_total)

        self.lbl_discount = QLabel("İskonto: 0.00 TL", self)
        self.lbl_discount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        totals_payments_layout.addWidget(self.lbl_discount)

        self.lbl_odenen_tutar = QLabel("Ödenen: 0.00 TL", self)
        self.lbl_odenen_tutar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        totals_payments_layout.addWidget(self.lbl_odenen_tutar)

        self.lbl_net_total = QLabel("Net Tutar: 0.00 TL", self)
        self.lbl_net_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_net_total.setStyleSheet("font-weight: bold; font-size: 12pt; color: blue;")
        totals_payments_layout.addWidget(self.lbl_net_total)

        self.lbl_kalan_tutar = QLabel("Kalan Tutar: 0.00 TL", self)
        self.lbl_kalan_tutar.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_kalan_tutar.setStyleSheet("font-weight: bold; color: red;")
        totals_payments_layout.addWidget(self.lbl_kalan_tutar)

        payment_buttons_widget = QWidget(self)
        payment_buttons_layout = QHBoxLayout(payment_buttons_widget)
        payment_buttons_layout.setContentsMargins(0, 5, 0, 0)

        self.btn_partial_payment = QPushButton("Parçalı Ödeme Al", self)
        self.btn_partial_payment.clicked.connect(self.process_partial_payment)
        self.btn_partial_payment.setObjectName("OdemeButton")
        payment_buttons_layout.addWidget(self.btn_partial_payment)

        self.btn_pay_cash = QPushButton("Nakit Öde (Kalan)", self)
        self.btn_pay_cash.clicked.connect(lambda: self.process_full_payment("Nakit"))
        self.btn_pay_cash.setObjectName("OdemeButton")
        payment_buttons_layout.addWidget(self.btn_pay_cash)

        self.btn_pay_card = QPushButton("Kart Öde (Kalan)", self)
        self.btn_pay_card.clicked.connect(lambda: self.process_full_payment("Kart"))
        self.btn_pay_card.setObjectName("OdemeButton")
        payment_buttons_layout.addWidget(self.btn_pay_card)

        self.btn_pay_balance = QPushButton("Bakiye Öde (Kalan)", self)
        self.btn_pay_balance.clicked.connect(lambda: self.process_full_payment("Müşteri Bakiyesinden"))
        self.btn_pay_balance.setObjectName("OdemeButton")
        payment_buttons_layout.addWidget(self.btn_pay_balance)

        totals_payments_layout.addWidget(payment_buttons_widget)

        bottom_controls_widget = QWidget(self) # Bu bir QWidget
        bottom_controls_layout = QHBoxLayout(bottom_controls_widget) # Bu, widget'a uygulanmış bir QHBoxLayout
        bottom_controls_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(bottom_controls_widget) # widget'ı ana layout'a ekliyor

    def _configure_styles(self):
        """PySide6 widget stillerini yapılandırır."""
        self.setStyleSheet("""
            #OdemeButton {
                background-color: #28a745;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            #OdemeButton:hover {
                background-color: #218838;
            }
            #OdemeButton:pressed {
                background-color: #1e7e34;
            }

            QPushButton#HizliSatisButton {
                 padding: 8px;
                 border: 1px solid #ccc;
                 border-radius: 4px;
                 text-align: center;
            }
             QPushButton#HizliSatisButton:hover {
                border-color: #007bff;
            }
        """)

    def load_data(self):
         """Adisyon sekmesi aktif olduğunda verileri yükler."""
         print("Adisyon sekmesi verileri yükleniyor...")
         self.update_aktif_masa_label()
         self.load_customer_combobox()
         self.load_categories_combobox()
         self.filter_hizli_satis_buttons()
         self.load_cart()

         self._update_button_states()


    def update_aktif_masa_label(self):
        """Aktif masa etiketini günceller."""
        if self.main_app.aktif_masa is not None:
            self.lbl_aktif_masa.setText(f"Aktif Masa: {self.main_app.aktif_masa}")
        else:
            self.lbl_aktif_masa.setText("Aktif Masa: Seçilmedi")

    def load_customer_combobox(self, clear_selection=False):
        """Müşteri atama Combobox'ını veritabanındaki müşterilerle doldurur."""
        customers = self.main_app.db_manager.get_all_customers()

        self.cmb_musteri_sec.clear()
        self._customer_list_data = []

        self.cmb_musteri_sec.addItem("-- Müşteri Seçilmedi --", None)
        self._customer_list_data.append({"id": None, "text": "-- Müşteri Seçilmedi --"})


        for c in customers:
            text = f"{c['ad_soyad']} ({c['telefon'] or 'Telefon Yok'})"
            self.cmb_musteri_sec.addItem(text, c['musteri_id'])
            self._customer_list_data.append({"id": c['musteri_id'], "text": text})


        if clear_selection or self.main_app.aktif_siparis_id is None:
            self.cmb_musteri_sec.setCurrentIndex(0)
            self._update_assigned_customer_label(None)
        else:
             order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
             if order_info and order_info['musteri_id'] is not None:
                  assigned_customer_id = order_info['musteri_id']
                  index = self.cmb_musteri_sec.findData(assigned_customer_id)
                  if index != -1:
                       self.cmb_musteri_sec.setCurrentIndex(index)
                       assigned_customer_text = self.cmb_musteri_sec.itemText(index)
                       self._update_assigned_customer_label_by_text(assigned_customer_text)
                  else:
                       self.cmb_musteri_sec.setCurrentIndex(0)
                       self._update_assigned_customer_label(None)
             else:
                 self.cmb_musteri_sec.setCurrentIndex(0)
                 self._update_assigned_customer_label(None)

    def _assign_customer_to_order(self):
        """Combobox'tan seçilen müşteriyi aktif siparişe atar veya atamayı kaldırır."""
        if self.main_app.aktif_siparis_id is None:
             QMessageBox.warning(self, "Uyarı", "Müşteri atamak için aktif bir adisyon olmalıdır.")
             return

        selected_customer_id = self.cmb_musteri_sec.currentData()
        selected_customer_text = self.cmb_musteri_sec.currentText()

        customer_name_for_message = "Yok"
        if selected_customer_id is not None:
             customer_name_for_message = selected_customer_text.split('(')[0].strip()


        success = self.main_app.db_manager.link_customer_to_order(self.main_app.aktif_siparis_id, selected_customer_id)

        if success:
             if selected_customer_id is not None:
                 QMessageBox.information(self, "Başarılı", f"Müşteri '{customer_name_for_message}' adisyona atandı.")
             else:
                 QMessageBox.information(self, "Başarılı", "Müşteri adisyondan kaldırıldı.")

             self._update_assigned_customer_label(selected_customer_id)
             if hasattr(self.main_app, 'masa_tab') and isinstance(self.main_app.masa_tab, MasaTabPyside):
                  self.main_app.masa_tab.load_masa_buttons()

        else:
             QMessageBox.critical(self, "Hata", "Müşteri atama/kaldırma sırasında bir hata oluştu.")
             self.load_cart()


    def _update_assigned_customer_label(self, musteri_id):
        """Atanan müşteri etiketini günceller (musteri_id'ye göre)."""
        if musteri_id is not None:
            customer = self.main_app.db_manager.get_customer_by_id(musteri_id)
            if customer:
                 musteri_ad_soyad = customer['ad_soyad']
                 self.lbl_atanan_musteri.setText(f"Atanan: {musteri_ad_soyad}")
            else:
                 self.lbl_atanan_musteri.setText(f"Atanan: Bilinmiyor (ID: {musteri_id})")
        else:
            self.lbl_atanan_musteri.setText("Atanan: Yok")

    def _update_assigned_customer_label_by_text(self, customer_text):
        """Atanan müşteri etiketini Combobox metnine göre günceller."""
        if customer_text and customer_text != "-- Müşteri Seçilmedi --":
             musteri_ad_soyad = customer_text.split('(')[0].strip()
             self.lbl_atanan_musteri.setText(f"Atanan: {musteri_ad_soyad}")
        else:
             self.lbl_atanan_musteri.setText("Atanan: Yok")


    def load_categories_combobox(self):
        """Kategori filtre Combobox'ını günceller."""
        categories = self.main_app.db_manager.get_all_categories()

        self.cmb_kategori_filter.clear()
        self.cmb_kategori_filter.addItem("Tümü", None)

        for cat in categories:
             self.cmb_kategori_filter.addItem(cat['adi'], cat['kategori_id'])

        self.cmb_kategori_filter.setCurrentIndex(0)


    def filter_hizli_satis_buttons(self):
        """Arama kutusu veya kategori seçimine göre hızlı satış butonlarını filtreler ve yeniden oluşturur."""
        print("Hızlı satış butonları filtreleniyor ve yükleniyor...")
        search_term = self.entry_search.text().strip().lower()
        selected_category_id = self.cmb_kategori_filter.currentData()

        while self.hizli_satis_grid_layout.count():
            item = self.hizli_satis_grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        urunler = self.main_app.db_manager.get_all_products(include_inactive=False)

        filtered_urunler = []
        for urun in urunler:
            urun_adi_lower = urun['adi'].lower()
            urun_kategori_id = urun['kategori_id']

            category_match = (selected_category_id is None or selected_category_id == urun_kategori_id)
            search_match = (search_term in urun_adi_lower)

            if category_match and search_match:
                filtered_urunler.append(urun)

        row, col = 0, 0
        max_cols = 6

        for urun in filtered_urunler:
            urun_id = urun['urun_id']
            urun_adi = urun['adi']
            urun_fiyat = urun['fiyat']
            urun_kategori_id = urun['kategori_id']

            button_text = f"{urun_adi}\n{urun_fiyat:.2f} TL"

            btn = QPushButton(button_text)
            btn.setObjectName("HizliSatisButton")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumSize(100, 80)


            if urun_kategori_id is not None and urun_kategori_id > 0:
                 color_index = (urun_kategori_id - 1) % len(constants.DEFAULT_CATEGORY_COLORS)
                 bg_color = constants.DEFAULT_CATEGORY_COLORS[color_index]

                 btn.setStyleSheet(f"""
                     QPushButton#HizliSatisButton {{
                         background-color: {bg_color};
                     }}
                      QPushButton#HizliSatisButton:hover {{
                         border-color: #007bff;
                     }}
                 """)


            btn.clicked.connect(lambda checked, id=urun_id, adi=urun_adi, fiyat=urun_fiyat, kat_id=urun_kategori_id: self.add_to_cart(id, adi, fiyat, kat_id))

            self.hizli_satis_grid_layout.addWidget(btn, row, col, 1, 1)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        for i in range(max_cols):
            self.hizli_satis_grid_layout.setColumnStretch(i, 1)

        print(f"Toplam {len(filtered_urunler)} adet hızlı satış butonu eklendi.")


    def add_to_cart(self, urun_id, urun_adi, urun_fiyat, kategori_id):
        """Sepete ürün ekler veya mevcut ürünün miktarını artırır (hızlı satış butonu için miktar 1 kullanılır)."""
        if self.main_app.aktif_masa is None:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce Masalar sekmesinden bir masa seçin.")
            return

        try:
            if self.main_app.aktif_siparis_id is None:
                siparis_id = self.main_app.db_manager.create_new_order(self.main_app.aktif_masa)
                if siparis_id is None:
                     QMessageBox.critical(self, "Hata", "Yeni sipariş oluşturulamadı.")
                     return
                self.main_app.aktif_siparis_id = siparis_id
                print(f"Yeni sipariş oluşturuldu. ID: {self.main_app.aktif_siparis_id} (Masa {self.main_app.aktif_masa})")
                # Masa tabı tamamlandıysa MasaTab.load_masa_buttons() çağrılacak
                if hasattr(self.main_app, 'masa_tab') and isinstance(self.main_app.masa_tab, MasaTabPyside):
                     self.main_app.masa_tab.load_masa_buttons()
                self.load_customer_combobox(clear_selection=True)

            existing_item_widget = None
            detay_id_to_update = None

            root_item = self.cart_treeview.invisibleRootItem()
            for i in range(root_item.childCount()):
                 item = root_item.child(i)
                 # Try to safely get the detail ID, handle potential errors
                 try:
                     item_detay_id = int(item.text(5))
                 except ValueError:
                     print(f"Hata: Treeview item'ında geçersiz detay_id değeri: {item.text(5)}")
                     item_detay_id = -1 # Use a value that won't match a real ID

                 item_urun_id = item.data(0, Qt.UserRole)

                 if item_urun_id is not None and item_urun_id == urun_id and item_detay_id != -1:
                      existing_item_widget = item
                      detay_id_to_update = item_detay_id
                      break

            if existing_item_widget:
                current_miktar = float(existing_item_widget.text(1))
                new_miktar = current_miktar + 1.0
                birim_fiyat = float(existing_item_widget.text(2).replace(" TL", ""))
                new_tutar = new_miktar * birim_fiyat

                success, updated_detay_id = self.main_app.db_manager.add_order_item(
                    self.main_app.aktif_siparis_id, urun_id, urun_adi, new_miktar, birim_fiyat, kategori_id, detay_id=detay_id_to_update
                )

                if success:
                    existing_item_widget.setText(1, f"{new_miktar}")
                    existing_item_widget.setText(3, f"{new_tutar:.2f}")
                    self._recalculate_and_update_totals()

            else:
                # Ürün sepette yok, yeni ürün olarak ekle. Miktar girişindeki değeri kullan.
                try:
                    # Miktar girişindeki değeri al, boş veya geçersizse 1.0 kullan
                    quantity_str = self.entry_quantity.text().strip()
                    if not quantity_str:
                        quantity = 1.0
                    else:
                        quantity = float(quantity_str)
                        if quantity <= 0:
                            QMessageBox.warning(self, "Uyarı", "Miktar pozitif bir sayı olmalıdır.")
                            return
                except ValueError:
                    QMessageBox.warning(self, "Uyarı", "Geçerli bir miktar girin.")
                    return

                # Aşağıdaki satırlar (except bloğundan sonraki)
                # try: ve except: satırlarıyla aynı girintide olmalı (12 boşluk)
                birim_fiyat = urun_fiyat
                tutar = quantity * birim_fiyat

                success, new_detay_id = self.main_app.db_manager.add_order_item(
                    self.main_app.aktif_siparis_id, urun_id, urun_adi, quantity, birim_fiyat, kategori_id, detay_id=None
                )

                if success:
                    self.load_cart()


        except Exception as e:
            # This catch is for errors *outside* the inner try blocks in this method
            print(f"Ürün sepete eklenirken/güncellenirken beklenmedik hata oluştu: {e}")
            # In a real app, more robust error handling might be needed
            QMessageBox.critical(self, "Hata", f"Ürün sepete eklenirken/güncellenirken beklenmedik hata oluştu: {e}\nLütfen uygulamayı yeniden başlatmayı deneyin.")
            # Attempt to reload cart just in case, but error state might be tricky
            self.load_cart()


    def _recalculate_and_update_totals(self):
        """TreeWidget'taki öğelere göre toplamları yeniden hesaplar ve UI'ı/Masa toplamlarını günceller."""
        current_brut_total = 0.0
        root_item = self.cart_treeview.invisibleRootItem()
        for i in range(root_item.childCount()):
             item = root_item.child(i)
             try:
                  item_tutar = float(item.text(3).replace(" TL", ""))
                  current_brut_total += item_tutar
             except ValueError:
                  print(f"Hata: Geçersiz tutar değeri treeview'de bulundu: {item.text(3)}")


        current_iskonto = 0.0
        current_odenen_tutar = 0.0

        if self.main_app.aktif_siparis_id is not None:
             order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
             if order_info:
                  current_iskonto = order_info['iskonto'] or 0.0
                  current_odenen_tutar = order_info['odenen_tutar'] or 0.0


        self.update_totals_labels(current_brut_total, current_iskonto, current_odenen_tutar)

        if self.main_app.aktif_masa is not None and self.main_app.aktif_siparis_id is not None:
            order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
            if order_info and order_info['durum'] == 'Açık':
                 self.main_app.db_manager.update_masa_totals(self.main_app.aktif_masa, current_brut_total, current_iskonto, current_odenen_tutar)
                 # Masa tabı tamamlandıysa MasaTab.load_masa_buttons() çağrılacak
                 if hasattr(self.main_app, 'masa_tab') and isinstance(self.main_app.masa_tab, MasaTabPyside):
                      self.main_app.masa_tab.load_masa_buttons()


    def load_cart(self):
        """Aktif masanın sepetini (sipariş detaylarını) TreeWidget'e yükler."""
        print("Sepet verileri yükleniyor...")
        self.cart_treeview.clear()

        current_musteri_id = None

        if self.main_app.aktif_siparis_id is not None:
            items = self.main_app.db_manager.get_order_details(self.main_app.aktif_siparis_id)

            for item in items:
                 ekleme_saat = datetime.strptime(item['ekleme_zamani'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S") if item['ekleme_zamani'] else ""

                 tree_item = QTreeWidgetItem(self.cart_treeview)
                 tree_item.setText(0, item['urun_adi'])
                 tree_item.setText(1, f"{item['miktar']}")
                 tree_item.setText(2, f"{item['birim_fiyat']:.2f} TL")
                 tree_item.setText(3, f"{item['tutar']:.2f} TL")
                 tree_item.setText(4, ekleme_saat)
                 tree_item.setText(5, str(item['detay_id']))

                 tree_item.setData(0, Qt.UserRole, item['urun_id'])

            order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
            if order_info:
                 current_musteri_id = order_info['musteri_id']

        self._recalculate_and_update_totals()
        print(f"Sepete {self.cart_treeview.topLevelItemCount()} adet öğe yüklendi.")

        self._update_assigned_customer_label(current_musteri_id)
        self.load_customer_combobox()

        self._update_button_states()


    def update_totals_labels(self, brut_total, discount_amount, odenen_tutar): # <<< Parametre adı 'odenen_tutar' olarak değiştirildi
        """Brüt Toplam, İskonto, Ödenen ve Kalan Tutar etiketlerini günceller."""
        net_total = brut_total - discount_amount
        # Düzeltme: kalan_tutar hesaplamasında da 'odenen_tutar' kullanıldı
        kalan_tutar = net_total - odenen_tutar

        self.lbl_brut_total.setText(f"Brüt Toplam: {brut_total:.2f} TL")
        self.lbl_discount.setText(f"İskonto: {discount_amount:.2f} TL")
        # Burası zaten doğru isme sahipti, şimdi parametre ile uyumlu
        self.lbl_odenen_tutar.setText(f"Ödenen: {odenen_tutar:.2f} TL")
        self.lbl_net_total.setText(f"Net Tutar: {net_total:.2f} TL")
        self.lbl_kalan_tutar.setText(f"Kalan Tutar: {kalan_tutar:.2f} TL")


    def remove_selected_cart_item(self):
        """Sepetten seçili ürünü siler."""
        selected_items = self.cart_treeview.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen sepetten silmek için bir ürün seçin.")
            return

        selected_item = selected_items[0]
        detay_id_to_delete = int(selected_item.text(5))

        if self.main_app.aktif_siparis_id is None:
             QMessageBox.critical(self, "Hata", "Aktif sipariş bulunamadı.")
             return

        reply = QMessageBox.question(self, "Onay", "Seçili ürünü sepetten silmek istediğinizden emin misiniz?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, _ = self.main_app.db_manager.remove_order_item(detay_id_to_delete, self.main_app.aktif_siparis_id)

            if success:
                 QMessageBox.information(self, "Başarılı", "Ürün sepetten silindi.")
                 self.load_cart()

    def clear_cart(self):
        """Aktif masanın sepetini tamamen temizler ve adisyonu iptal eder."""
        if self.main_app.aktif_siparis_id is None:
            QMessageBox.information(self, "Bilgi", "Sepet zaten boş.")
            return

        reply = QMessageBox.question(self, "Onay", "Sepeti tamamen temizlemek istediğinizden emin misiniz? Bu işlem adisyonu iptal eder.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success = self.main_app.db_manager.clear_order_details(self.main_app.aktif_siparis_id)

            if success:
                QMessageBox.information(self, "Başarılı", "Sepet temizlendi ve adisyon iptal edildi.")
                self.main_app.aktif_masa = None
                self.main_app.aktif_siparis_id = None
                self.update_aktif_masa_label()
                self.cart_treeview.clear()
                self.update_totals_labels(0.0, 0.0, 0.0)
                self.load_customer_combobox(clear_selection=True)
                self._update_assigned_customer_label(None)

                # Masa tabı tamamlandıysa MasaTab.load_masa_buttons() çağrılacak
                if hasattr(self.main_app, 'masa_tab') and isinstance(self.main_app.masa_tab, MasaTabPyside):
                     self.main_app.masa_tab.load_masa_buttons()

                self._update_button_states()


    def apply_discount(self):
        """Aktif masanın adisyonına iskonto uygular."""
        if self.main_app.aktif_siparis_id is None:
            QMessageBox.warning(self, "Uyarı", "İskonto uygulamak için aktif bir adisyon olmalıdır.")
            return

        order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
        if not order_info:
             QMessageBox.critical(self, "Hata", "Adisyon bilgisi alınamadı.")
             return

        current_brut_total = order_info['toplam_tutar'] or 0.0

        if current_brut_total <= 0:
             QMessageBox.warning(self, "Uyarı", "İskonto uygulamak için sepette ürün olmalı veya brüt toplam sıfırdan büyük olmalıdır.")
             return

        dialog = DiscountDialogPyside(self, current_brut_total)
        result = dialog.exec()

        if result == QDialog.Accepted:
            discount_amount = dialog.get_discount_amount()

            if discount_amount is not None:
                 if discount_amount > current_brut_total:
                      QMessageBox.warning(self, "Uyarı", f"İskonto miktarı brüt toplamdan ({current_brut_total:.2f} TL) fazla olamaz.")
                      return

                 success = self.main_app.db_manager.update_order_discount(self.main_app.aktif_siparis_id, discount_amount)

                 if success:
                     QMessageBox.information(self, "Başarılı", f"{discount_amount:.2f} TL iskonto uygulandı.")
                     self._recalculate_and_update_totals()

        else:
             QMessageBox.information(self, "Bilgi", "İskonto işlemi iptal edildi.")


    def process_partial_payment(self):
         """Parçalı ödeme işlemini başlatır."""
         if self.main_app.aktif_siparis_id is None:
             QMessageBox.warning(self, "Uyarı", "Parçalı ödeme almak için aktif bir adisyon olmalıdır.")
             return

         order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
         if not order_info:
              QMessageBox.critical(self, "Hata", "Adisyon bilgisi alınamadı.")
              return

         brut_toplam = order_info['toplam_tutar'] or 0.0
         iskonto = order_info['iskonto'] or 0.0
         odenen_tutar_current = order_info['odenen_tutar'] or 0.0
         net_toplam = brut_toplam - iskonto
         kalan_tutar = net_toplam - odenen_tutar_current

         if kalan_tutar <= 0 and odenen_tutar_current >= net_toplam:
              QMessageBox.information(self, "Bilgi", f"Ödenecek kalan tutar yok. Bu adisyon zaten {odenen_tutar_current:.2f} TL ile kapatılmış.")
              return

         dialog = PartialPaymentDialogPyside(self, kalan_tutar)
         result = dialog.exec()

         if result == QDialog.Accepted:
             payment_amount = dialog.get_payment_amount()

             if payment_amount is not None and payment_amount > 0:

                 success = self.main_app.db_manager.record_partial_payment(self.main_app.aktif_siparis_id, payment_amount, payment_method="Ara Ödeme")

                 if success:
                     QMessageBox.information(self, "Başarılı", f"{payment_amount:.2f} TL parçalı ödeme alındı.")
                     self._recalculate_and_update_totals()

             elif payment_amount is not None and payment_amount <= 0:
                 QMessageBox.warning(self, "Uyarı", "Ödeme miktarı pozitif bir sayı olmalıdır.")

         else:
             QMessageBox.information(self, "Bilgi", "Parçalı ödeme işlemi iptal edildi.")


    def process_full_payment(self, payment_method):
        """Adisyonun kalan tutarını kapatır ve ödeme işlemini tamamlar."""
        if self.main_app.aktif_siparis_id is None:
            QMessageBox.warning(self, "Uyarı", "Ödeme almak için aktif bir adisyon olmalıdır.")
            return

        order_info = self.main_app.db_manager.get_order_info(self.main_app.aktif_siparis_id)
        if not order_info:
             QMessageBox.critical(self, "Hata", "Adisyon bilgisi alınamadı.")
             return

        brut_toplam = order_info['toplam_tutar'] or 0.0
        iskonto = order_info['iskonto'] or 0.0
        odenen_tutar_current = order_info['odenen_tutar'] or 0.0
        net_toplam = brut_toplam - iskonto
        # DÜZELTİLDİ: odenen_toplam yerine odenen_tutar_current kullanıldı
        kalan_tutar = net_toplam - odenen_tutar_current

        if kalan_tutar <= 0 and odenen_tutar_current >= net_toplam:
             QMessageBox.information(self, "Bilgi", f"Bu adisyon zaten {odenen_tutar_current:.2f} TL ile kapatılmış veya ödenecek kalan tutar yok.")
             self._update_button_states()
             return


        confirm_message = f"Masa {self.main_app.aktif_masa} için kalan {kalan_tutar:.2f} TL tutarını ({payment_method}) ile kapatmak istediğinizden emin misiniz?"
        if odenen_tutar_current > 0:
             confirm_message = f"Masa {self.main_app.aktif_masa} için kalan {kalan_tutar:.2f} TL tutarını ({payment_method}) ile kapatmak istediğinizden (Toplam ödenen: {odenen_tutar_current:.2f} TL) emin misiniz? (Daha önce {odenen_tutar_current:.2f} TL ödeme alınmıştır.)"


        reply = QMessageBox.question(self, "Ödeme Onayı", confirm_message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if payment_method == "Müşteri Bakiyesinden":
                 if order_info['musteri_id'] is None:
                      QMessageBox.warning(self, "Uyarı", "Adisyona atanmış bir müşteri olmadan bakiyeden ödeme yapılamaz.")
                      return

                 customer_id = order_info['musteri_id']
                 customer_info = self.main_app.db_manager.get_customer_by_id(customer_id)
                 if customer_info is None:
                      QMessageBox.critical(self, "Hata", "Atanan müşteri bilgisi bulunamadı.")
                      return

                 customer_balance = customer_info['bakiye'] or 0.0

                 if customer_balance < kalan_tutar:
                      QMessageBox.warning(self, "Uyarı", f"Müşterinin bakiyesi yetersiz. (Bakiye: {customer_balance:.2f} TL, Kalan: {kalan_tutar:.2f} TL)")
                      return

                 success_balance = self.main_app.db_manager.update_customer_balance(customer_id, -kalan_tutar)
                 if not success_balance:
                      QMessageBox.critical(self, "Hata", "Müşteri bakiyesi düşülürken bir hata oluştu.")
                      return

            success, final_net_total = self.main_app.db_manager.process_full_payment(self.main_app.aktif_siparis_id, payment_method)

            if success:
                QMessageBox.information(self, "Başarılı", f"Masa {self.main_app.aktif_masa} için ödeme alındı. Net Toplam: {final_net_total:.2f} TL ({payment_method})")

                self.main_app.aktif_masa = None
                self.main_app.aktif_siparis_id = None
                self.update_aktif_masa_label()
                self.cart_treeview.clear()
                self.update_totals_labels(0.0, 0.0, 0.0)
                self.load_customer_combobox(clear_selection=True)
                self._update_assigned_customer_label(None)

                # Masa tabı tamamlandıysa MasaTab.load_masa_buttons() çağrılacak
                if hasattr(self.main_app, 'masa_tab') and isinstance(self.main_app.masa_tab, MasaTabPyside):
                     self.main_app.masa_tab.load_masa_buttons()

                self._update_button_states()


    # adisyon_tab_pyside.py içinde, _update_button_states metodu
    def _update_button_states(self):
        """Aktif masa veya sepet durumuna göre butonların aktifliğini ayarlar."""
        is_masa_selected = self.main_app.aktif_masa is not None
        is_order_open = self.main_app.aktif_siparis_id is not None
        is_cart_empty = self.cart_treeview.topLevelItemCount() == 0

        self.btn_apply_discount.setEnabled(is_order_open and not is_cart_empty)
        self.btn_clear_cart.setEnabled(is_order_open and not is_cart_empty)
        # Düzeltme: selectedItems() sonucunu bool() ile True/False'a çevir
        self.btn_remove_selected.setEnabled(is_order_open and bool(self.cart_treeview.selectedItems()) and not is_cart_empty) # <<< Bu satırı düzeltin

        self.btn_partial_payment.setEnabled(is_order_open and not is_cart_empty)
        self.btn_pay_cash.setEnabled(is_order_open and not is_cart_empty)
        self.btn_pay_card.setEnabled(is_order_open and not is_cart_empty)
        self.btn_pay_balance.setEnabled(is_order_open and not is_cart_empty)

        self.btn_atama_yap.setEnabled(is_order_open)