from PySide6.QtCore import QCoreApplication, QRect, QSize, Qt, QMetaObject, QTimer
from PySide6.QtGui import QIntValidator, QFont, QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QToolTip, QGroupBox, QPushButton, QComboBox, QCheckBox, QWidget
import os
import pygetwindow as gw
from pywinauto import Application
import threading
import requests

class UserProfileDialog(QDialog):
    def __init__(self, discord_user_id):
        super().__init__()
        self.setWindowTitle("User Profile")
        self.setFixedSize(200, 200)
        self.setStyleSheet("background-color: #333; color: #fff;")

        self.discord_user_id = discord_user_id
        self.profile_picture_label = QLabel(self)
        self.profile_picture_label.setGeometry(QRect(50, 50, 100, 100))

        self.load_profile_picture()

    def load_profile_picture(self):
        # Discord API'den profil fotoğrafını al ve göster
        profile_picture_url = f"https://cdn.discordapp.com/avatars/{self.discord_user_id}/avatar.png"
        response = requests.get(profile_picture_url)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.profile_picture_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

class AutoSkillDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Skill Settings")
        self.setFixedSize(200, 160)
        self.setStyleSheet("background-color: #333; color: #fff;")

        self.label_7 = QLabel("Auto Skill", self)
        self.label_7.setGeometry(QRect(50, 0, 101, 31))
        font = self.label_7.font()
        font.setFamily("Iceland")
        font.setPointSize(20)
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Interval time:", self)
        self.label.setGeometry(QRect(10, 40, 91, 31))
        font.setPointSize(12)
        self.label.setFont(font)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QRect(110, 43, 51, 24))
        self.lineEdit.setValidator(QIntValidator(0, 3600))
        self.lineEdit.setStyleSheet("background-color: #555; color: #fff;")

        self.label_2 = QLabel("Skill Keys:", self)
        self.label_2.setGeometry(QRect(10, 80, 71, 21))
        self.label_2.setFont(font)
        self.label_2.setToolTip("Only the keys in the range of 1 to 4.")
        QToolTip.setFont(QFont('SansSerif', 10))

        skill_key_validator = QIntValidator(1, 4, self)

        self.lineEdit_2 = QLineEdit(self)
        self.lineEdit_2.setGeometry(QRect(90, 82, 21, 21))
        self.lineEdit_2.setValidator(skill_key_validator)
        self.lineEdit_2.setStyleSheet("background-color: #555; color: #fff;")

        self.lineEdit_3 = QLineEdit(self)
        self.lineEdit_3.setGeometry(QRect(120, 82, 21, 21))
        self.lineEdit_3.setValidator(skill_key_validator)
        self.lineEdit_3.setStyleSheet("background-color: #555; color: #fff;")

        self.lineEdit_4 = QLineEdit(self)
        self.lineEdit_4.setGeometry(QRect(150, 82, 21, 21))
        self.lineEdit_4.setValidator(skill_key_validator)
        self.lineEdit_4.setStyleSheet("background-color: #555; color: #fff;")

        self.pushButton = QPushButton("ACCEPT", self)
        self.pushButton.setGeometry(QRect(60, 120, 80, 24))
        self.pushButton.setStyleSheet("background-color: #555; color: #fff;")
        self.pushButton.clicked.connect(self.accept)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = None
        self.window_title = None
        self.selected_model_path = None
        self.model = None
        self.skill_activation_interval = 300
        self.skill_keys = ['1', '2']
        self.pause_event = threading.Event()
        self.text_break_event = threading.Event()
        self.text_break_event.set()
        self.killed_stones_count = 0  # Sayaç değişkeni
        self.discord_user_id = "1347394490121588839"

    def setupUi(self, Widget):
        Widget.setObjectName("MysTBot")
        Widget.setStyleSheet("background-color: #333; color: #fff;")
        Widget.resize(530, 330)
        Widget.setMinimumSize(QSize(530, 330))
        Widget.setMaximumSize(QSize(530, 330))
        Widget.setAutoFillBackground(False)

        self.groupBox_Farm = QGroupBox(Widget)
        self.groupBox_Farm.setObjectName("groupBox_Farm")
        self.groupBox_Farm.setGeometry(QRect(20, 40, 240, 121))

        self.pushButton = QPushButton(self.groupBox_Farm)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(10, 20, 80, 24))
        self.pushButton.setStyleSheet("background-color: #555; color: #fff;")

        self.pushButton_2 = QPushButton(self.groupBox_Farm)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(100, 20, 80, 24))
        self.pushButton_2.setStyleSheet("background-color: #555; color: #fff;")

        self.label = QLabel(self.groupBox_Farm)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 55, 60, 15))

        self.lineEdit = QLineEdit(self.groupBox_Farm)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setGeometry(QRect(70, 55, 31, 21))
        self.lineEdit.setReadOnly(False)
        self.lineEdit.setValidator(QIntValidator(0, 999))
        self.lineEdit.setStyleSheet("background-color: #555; color: #fff;")

        self.label_2 = QLabel(self.groupBox_Farm)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(130, 100, 101, 16))

        font = self.label_2.font()  # Font değişkeni burada tanımlanıyor
        font.setPointSize(9)

        self.killed_stones_label = QLabel("0", self.groupBox_Farm)  # Sayaç etiketi
        self.killed_stones_label.setObjectName("killed_stones_label")
        self.killed_stones_label.setGeometry(QRect(202, 100, 25, 16))  # Etiketin yerini ve boyutunu ayarlayın
        self.killed_stones_label.setFont(font)
        self.killed_stones_label.setStyleSheet("color: #fff;")

        self.groupBox_Features = QGroupBox(Widget)
        self.groupBox_Features.setObjectName("groupBox_Features")
        self.groupBox_Features.setGeometry(QRect(20, 160, 240, 121))

        self.checkBox = QCheckBox(self.groupBox_Features)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setGeometry(QRect(10, 30, 91, 22))

        self.checkBox_2 = QCheckBox(self.groupBox_Features)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_2.setGeometry(QRect(10, 50, 91, 22))

        self.auto_skill_button = QPushButton(self.groupBox_Features)
        self.auto_skill_button.setObjectName("auto_skill_button")
        self.auto_skill_button.setGeometry(QRect(150, 50, 80, 24))
        self.auto_skill_button.setStyleSheet("background-color: #555; color: #fff;")
        self.auto_skill_button.setText("A-S Settings")

        self.checkBox_3 = QCheckBox(self.groupBox_Features)
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_3.setGeometry(QRect(10, 70, 101, 22))

        self.groupBox_Farm_2 = QGroupBox(Widget)
        self.groupBox_Farm_2.setObjectName("groupBox_Farm_2")
        self.groupBox_Farm_2.setGeometry(QRect(270, 40, 240, 121))

        self.pushButton_5 = QPushButton(self.groupBox_Farm_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(10, 55, 71, 21))
        self.pushButton_5.setStyleSheet("background-color: #555; color: #fff;")

        self.comboBox = QComboBox(self.groupBox_Farm_2)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(90, 55, 141, 21))
        self.comboBox.setStyleSheet("background-color: #555; color: #fff;")
        
        self.pid_combobox = self.comboBox  # Bind comboBox to pid_combobox for compatibility

        self.label_5 = QLabel(self.groupBox_Farm_2)
        self.label_5.setObjectName("label_5")
        self.label_5.setGeometry(QRect(90, 35, 141, 16))

        self.label_6 = QLabel(self.groupBox_Farm_2)
        self.label_6.setObjectName("label_6")
        self.label_6.setGeometry(QRect(90, 80, 141, 16))

        self.groupBox_Farm_3 = QGroupBox(Widget)
        self.groupBox_Farm_3.setObjectName("groupBox_Farm_3")
        self.groupBox_Farm_3.setGeometry(QRect(270, 160, 240, 121))

        self.comboBox_2 = QComboBox(self.groupBox_Farm_3)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.setGeometry(QRect(10, 30, 221, 21))
        self.comboBox_2.setEditable(False)
        self.comboBox_2.setDuplicatesEnabled(False)
        self.comboBox_2.setStyleSheet("background-color: #555; color: #fff;")

        self.label_7 = QLabel(Widget)
        self.label_7.setObjectName("label_7")
        self.label_7.setGeometry(QRect(20, 0, 101, 31))
        font = self.label_7.font()
        font.setFamily("Iceland")
        font.setPointSize(20)
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.text_break_time_edit = QLineEdit(self.groupBox_Farm)
        self.text_break_time_edit.setGeometry(QRect(70, 55, 31, 21))
        self.text_break_time_edit.setValidator(QIntValidator(0, 999))
        self.text_break_time_edit.setStyleSheet("background-color: #555; color: #fff;")

        self.timer = QTimer(self)  # Timer oluşturuldu
        self.timer.timeout.connect(self.update_pid_list)
        self.timer.setInterval(15000)  # 30 saniyede bir çalışacak şekilde ayarlandı
        self.timer.start()

        # Kapatma butonu (❌)
        self.close_button = QPushButton("❌", self)
        self.close_button.setGeometry(self.width() - 40, 0, 30, 30)
        self.close_button.setStyleSheet("background-color: #555; color: #fff;")
        self.close_button.clicked.connect(self.close)

        # Küçültme butonu (➖)
        self.minimize_button = QPushButton("➖", self)
        self.minimize_button.setGeometry(self.width() - 80, 0, 30, 30)
        self.minimize_button.setStyleSheet("background-color: #555; color: #fff;")
        self.minimize_button.clicked.connect(self.showMinimized)

        # Ayarlar butonu (⚙️)
        self.settings_button = QPushButton("⚙️", self)
        self.settings_button.setGeometry(self.width() - 120, 0, 30, 30)
        self.settings_button.setStyleSheet("background-color: #555; color: #fff;")
        self.settings_button.clicked.connect(self.open_user_profile_dialog)

        self.retranslateUi(Widget)
        QMetaObject.connectSlotsByName(Widget)

        self.comboBox_2.currentIndexChanged.connect(self.on_folder_selected)

        self.update_model_combobox()

    def list_model_folders(self):
        models_path = "models"
        try:
            folders = [f.name for f in os.scandir(models_path) if f.is_dir()]
            return folders
        except FileNotFoundError:
            print(f"'{models_path}' klasörü bulunamadı.")
            return []

    def on_folder_selected(self):
        selected_folder = self.comboBox_2.currentText()
        if selected_folder and selected_folder != "Select Map":
            files = self.list_files_in_folder(selected_folder)
            self.create_or_update_file_combobox(files)

    def list_files_in_folder(self, folder):
        folder_path = os.path.join("models", folder)
        try:
            files = [os.path.splitext(f.name)[0] for f in os.scandir(folder_path) if f.is_file()]
            return files
        except FileNotFoundError:
            print(f"'{folder_path}' directory not found.")
            return []

    def create_or_update_file_combobox(self, files):
        if hasattr(self, 'file_combobox'):
            self.file_combobox.clear()
            self.file_combobox.addItems(files)
        else:
            self.file_combobox = QComboBox(self.groupBox_Farm_3)
            self.file_combobox.setGeometry(QRect(10, 60, 221, 21))
            self.file_combobox.setStyleSheet("background-color: #555; color: #fff;")
            self.file_combobox.addItems(files)
            self.file_combobox.show()

        self.file_combobox.currentIndexChanged.connect(self.on_file_selected)    

    def on_file_selected(self):
        selected_folder = self.comboBox_2.currentText()
        selected_file = self.file_combobox.currentText()
        if selected_folder and selected_file:
            self.selected_model_path = os.path.join("models", selected_folder, selected_file + ".pt")    

    def update_model_combobox(self):
        folders = self.list_model_folders()
        self.comboBox_2.clear()
        self.comboBox_2.addItem("Select Map")
        self.comboBox_2.addItems(folders)
        self.comboBox_2.setCurrentIndex(0)

    def update_pid_list(self):
        current_pid = self.comboBox.currentText()
        self.comboBox.clear()
        self.comboBox.addItem("Select PID")
        windows = gw.getWindowsWithTitle('')
        for window in windows:
            if window.title:
                print(f"Adding window: {window.title} ({window._hWnd})")
                self.comboBox.addItem(f"{window.title} ({window._hWnd})", window._hWnd)

        index = self.comboBox.findText(current_pid)
        if index != -1:
            self.comboBox.setCurrentIndex(index)

    def update_window_title(self):
        selected_pid = self.comboBox.currentData()
        if selected_pid:
            self.window_title = int(selected_pid)
            print(f"Selected PID: {self.window_title}")
        else:
            print("Lütfen bir pencere seçin.")

    def accept_window_title(self):
        self.update_window_title()
        self.timer.stop()  # Timer'ı durdur

    def open_auto_skill_dialog(self):
        dialog = AutoSkillDialog()
        if dialog.exec():
            try:
                self.skill_activation_interval = int(dialog.lineEdit.text())
                print("Interval time set to:", self.skill_activation_interval)
            except ValueError:
                print("Geçerli bir interval süresi girin.")
            self.skill_keys = [dialog.lineEdit_2.text(), dialog.lineEdit_3.text(), dialog.lineEdit_4.text()]
            print("Skill keys:", self.skill_keys)

    def open_user_profile_dialog(self):
        dialog = UserProfileDialog(self.discord_user_id)
        dialog.exec()        

    def start_main_functionality(self):
        if self.selected_model_path is None:
            print("Model path is not selected.")
            return

        if not self.window_title or self.window_title == "Select PID":
            print("Lütfen bir pencere seçin.")
            return

        try:
            text_break_time = int(self.text_break_time_edit.text())
        except ValueError:
            print("Geçerli bir metin kırma süresi girin.")
            return

        print(f"Başlatılıyor: window_title={self.window_title}, text_break_time={text_break_time}")

        # Diğer gerekli işlevleri burada başlatabilirsiniz

    def stop_functionality(self):  # Stop işlevi eklendi
        self.pause_event.set()
        print("Durduruldu.")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = None

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(QCoreApplication.translate("Widget", "MysTBot", None))
        Widget.setWindowIcon(QIcon("acs.ico"))
        self.groupBox_Farm.setTitle(QCoreApplication.translate("Widget", "Farm", None))
        self.pushButton.setText(QCoreApplication.translate("Widget", "START", None))
        self.pushButton_2.setText(QCoreApplication.translate("Widget", "STOP", None))
        self.label.setText(QCoreApplication.translate("Widget", "Metin sec:", None))
        self.lineEdit.setText("")
        self.label_2.setText(QCoreApplication.translate("Widget", "Killed Stones:", None))
        self.groupBox_Features.setTitle(QCoreApplication.translate("Widget", "Features", None))
        self.checkBox.setText(QCoreApplication.translate("Widget", "Auto Pickup", None))
        self.checkBox_2.setText(QCoreApplication.translate("Widget", "Auto Skill", None))
        self.checkBox_3.setText(QCoreApplication.translate("Widget", "Captcha Solver", None))
        self.groupBox_Farm_2.setTitle(QCoreApplication.translate("Widget", "Client 1024x768", None))
        self.pushButton_5.setText(QCoreApplication.translate("Widget", "ACCEPT", None))
        self.label_5.setText(QCoreApplication.translate("Widget", "Refreshes every 15 seconds", None))
        self.label_6.setText(QCoreApplication.translate("Widget", "1024x768 Client PID input", None))
        self.groupBox_Farm_3.setTitle(QCoreApplication.translate("Widget", "Select Metinstones", None))
        self.label_7.setText(QCoreApplication.translate("Widget", "MysTBot", None))