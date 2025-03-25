import sys
from PySide6.QtWidgets import QApplication
from gui.ui import MyApp
import gui.functions as functions
from PySide6.QtCore import QTimer
from login import LoginWindow  # LoginWindow sınıfını içe aktarın

def main():
    app = QApplication(sys.argv)

    # Login penceresini gösterin
    login_window = LoginWindow()
    login_window.show()

    # Giriş başarılı olduğunda ana uygulamayı başlatın
    def start_main_app():
        window = MyApp()
        window.show()

        window.auto_skill_button.clicked.connect(window.open_auto_skill_dialog)
        window.pushButton_5.clicked.connect(window.accept_window_title)
        window.pushButton.clicked.connect(lambda: functions.start_main_functionality(window))
        window.pushButton_2.clicked.connect(lambda: functions.stop_functionality(window))
        window.comboBox.currentIndexChanged.connect(window.update_window_title)
        window.timer.timeout.connect(lambda: functions.update_pid_list(window.pid_combobox))
        window.close_button.clicked.connect(window.close)
        window.minimize_button.clicked.connect(window.showMinimized)

    # Login penceresinin başarılı giriş sinyaline bağlanın
    login_window.main_app_opened.connect(start_main_app)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()