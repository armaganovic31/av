import logging
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QApplication
from PySide6.QtGui import QFont, QMouseEvent, QPainterPath, QRegion
from PySide6.QtCore import Qt, Signal, QRect

import sys
import requests
from utils import validate_license_key, check_user_role

# Günlük kayıtlarını ayarlayın
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Çalışma dizinini belirleyin
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

class LoginWindow(QWidget):
    main_app_opened = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MysT Bot")
        self.setFixedSize(350, 300)
        self.setStyleSheet("background-color: #2D2D2D; border-radius: 20px;")  # border-radius ekledik
        
        # Üst paneli kaldır (çerçevesiz pencere)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Pencerenin köşelerini gerçekten oval yapmak için maske uygula
        self.set_masked_rounded_corners()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Kenar boşluklarını kaldır

        # Özel Başlık Çubuğu (Kapatma ve Alta Alma Butonları ile)
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("")
        self.title_label.setFont(QFont("Montserrat", 10))
        self.title_label.setStyleSheet("color: white;")
        self.title_label.setAlignment(Qt.AlignLeft)

        # Alta Alma Butonu
        self.minimize_button = QPushButton("➖")
        self.minimize_button.setFixedSize(20, 20)
        self.minimize_button.setStyleSheet("background: none; color: white; font-size: 14px; border: none;")
        self.minimize_button.clicked.connect(self.showMinimized)

        # Kapatma Butonu
        self.close_button = QPushButton("❌")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("background: none; color: white; font-size: 14px; border: none;")
        self.close_button.clicked.connect(self.close)

        title_bar.addWidget(self.title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.minimize_button)
        title_bar.addWidget(self.close_button)

        main_layout.addLayout(title_bar)

        # Ana İçerik
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 0, 20, 10)

        # Title Label
        title_label = QLabel("MysT Bot")
        title_label.setFont(QFont("Iceland", 35, QFont.Normal))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setContentsMargins(0, -10, 0, 0)
        content_layout.addWidget(title_label)

        # Login Label
        login_label = QLabel("Login")
        login_label.setFont(QFont("Iceland", 25, QFont.Normal))
        login_label.setStyleSheet("color: white;")
        login_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(login_label)

        # Input Field for License Key
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your license key")
        self.key_input.setFont(QFont("Montserrat", 12))
        self.key_input.setStyleSheet("background-color: #3E3E3E; color: white; padding: 10px; border-radius: 5px;")
        self.key_input.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(self.key_input)

        # Input Field for Discord ID
        self.discord_id_input = QLineEdit()
        self.discord_id_input.setPlaceholderText("Enter your Discord ID")
        self.discord_id_input.setFont(QFont("Montserrat", 12))
        self.discord_id_input.setStyleSheet("background-color: #3E3E3E; color: white; padding: 10px; border-radius: 5px;")
        self.discord_id_input.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(self.discord_id_input)

        # Login Button
        login_button = QPushButton("LOGIN")
        login_button.setFont(QFont("Montserrat", 12))
        login_button.setStyleSheet("background-color: #A0E0C0; padding: 10px; border-radius: 5px; font-weight: bold;")
        login_button.clicked.connect(self.handle_login)
        content_layout.addWidget(login_button)

        # Footer Label
        footer_label = QLabel('<span style="color:white;">Do you need a key?</span> <a href="https://discord.gg/eFAE4JNjQ7" style="color:#7289DA; text-decoration:none;"><b>Discord.</b></a>')
        footer_label.setFont(QFont("Montserrat", 10))
        footer_label.setStyleSheet("color: white;")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setOpenExternalLinks(True)
        content_layout.addWidget(footer_label)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Pencere sürükleme için başlangıç noktası
        self.old_pos = None

    def handle_login(self):
        """Login butonuna basıldığında çağrılır ve lisans doğrulaması yapar"""
        token = self.key_input.text()
        discord_user_id = self.discord_id_input.text()
        if discord_user_id:
            logging.debug(f'Giriş denemesi: {token} - Discord User ID: {discord_user_id}')
            
            is_valid, message = validate_license_key(token, discord_user_id)
            if is_valid:
                if check_user_role(discord_user_id):
                    self.key_input.setStyleSheet("background-color: #3E3E3E; color: white; padding: 10px; border-radius: 5px;")
                    logging.info("Giriş başarılı!")
                    self.show_success_message(message)
                    self.main_app_opened.emit()  # Giriş başarılı sinyalini yayınla
                    self.close()  # Login penceresini kapat
                else:
                    self.key_input.setStyleSheet("background-color: #3E3E3E; color: red; padding: 10px; border-radius: 5px;")
                    logging.warning("Gerekli role sahip değilsiniz.")
                    self.show_error_message("Gerekli role sahip değilsiniz.")
            else:
                self.key_input.setStyleSheet("background-color: #3E3E3E; color: red; padding: 10px; border-radius: 5px;")
                logging.warning("Geçersiz token veya Discord User ID. Giriş başarısız.")
                self.show_error_message(message)
        else:
            logging.warning("Discord kimlik doğrulaması başarısız.")
            self.show_error_message("Discord kimlik doğrulaması başarısız.")

    def show_success_message(self, message):
        """Giriş başarılı olduğunda uyarı mesajı gösterir"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Başarılı")
        msg.exec()

    def show_error_message(self, message):
        """Giriş başarısız olduğunda uyarı mesajı gösterir"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Hata")
        msg.exec()

    def set_masked_rounded_corners(self):
        """Pencerenin köşelerini gerçekten oval yapar"""
        path = QPainterPath()
        rect = QRect(0, 0, self.width(), self.height())
        radius = 20  # Köşe ovalleştirme derecesi
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        """Pencere boyutu değişirse maskeyi tekrar uygula"""
        self.set_masked_rounded_corners()

    def mousePressEvent(self, event: QMouseEvent):
        """Fare tıklanınca başlangıç pozisyonunu kaydet"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Fare hareket ettikçe pencereyi yeni konuma taşır"""
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Fare bırakıldığında sürükleme işlemini durdur"""
        if event.button() == Qt.LeftButton:
            self.old_pos = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())