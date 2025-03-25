import threading
import time
import psutil
from pywinauto import Application
from functions.capture_screen import capture_window_by_pid, get_hwnd_by_pid
from functions.yolo_detection import detect_objects, draw_detections, get_closest_detection_center, load_model, DISTANCE_THRESHOLD
from functions.mouse_events import move_mouse, click_mouse
from functions.metinstones_break import text_break
from functions.rotate_screen import rotate_screen_periodically, check_and_rotate_screen
from functions.activate_skill import activate_skills, activate_skills_periodically
from functions.captcha_solver import capture_captcha_and_solve
from functions.auto_pickup import auto_pickup
from functions.auto_revive import auto_revive

def update_pid_list(pid_combobox):
    current_pid = pid_combobox.currentText()
    pid_combobox.clear()
    pid_combobox.addItem("Select PID")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['pid']:
                hwnd = get_hwnd_by_pid(proc.info['pid'])
                if hwnd:
                    pid_combobox.addItem(f"{proc.info['name']} ({proc.info['pid']})", proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    index = pid_combobox.findText(current_pid)
    if index != -1:
        pid_combobox.setCurrentIndex(index)

def update_window_title(pid_combobox, window_title):
    selected_pid = pid_combobox.currentData()
    if selected_pid:
        window_title = int(selected_pid)
        print(f"Selected PID: {window_title}")
    else:
        print("Lütfen bir pencere seçin.")
    return window_title

def focus_and_move_window(window_title):
    if window_title and window_title != "Select PID":
        try:
            app = Application().connect(process=window_title)
            window = app.top_window()
            window.set_focus()
            window.move_window(0, 0)
        except Exception as e:
            print(f"Pencere taşınamadı: {e}")
    else:
        print("Lütfen bir pencere seçin.")

def start_main_functionality(window):
    if window.selected_model_path is None:
        print("Model path is not selected.")
        return

    model = load_model(window.selected_model_path)        

    if not window.window_title or window.window_title == "Select PID":
        print("Lütfen bir pencere seçin.")
        return

    try:
        text_break_time = int(window.text_break_time_edit.text())
    except ValueError:
        print("Geçerli bir metin kırma süresi girin.")
        return

    print(f"Başlatılıyor: window_title={window.window_title}, text_break_time={text_break_time}")

    captcha_check_interval = 0.1
    stop_event = threading.Event()

    def main_loop():
        # Bot başlatıldığında skill açma işlemi
        if window.checkBox_2.isChecked():
            activate_skills(window.pause_event, window.text_break_event, window.skill_keys)

        last_skill_activation_time = time.time()

        while not stop_event.is_set():
            try:
                print(f"Ekran görüntüsü alınıyor... PID: {window.window_title}")
                image = capture_window_by_pid(window.window_title)
                if image is None:
                    print(f"PID {window.window_title} için ekran görüntüsü alınamadı.")
                    continue

                print("Nesne tespiti yapılıyor...")
                results = detect_objects(image, model)

                num_detections = sum(1 for result in results for box in result.boxes if model.names[int(box.cls[0])] != 'none')
                print(f"{num_detections} nesne tespit edildi.")

                if num_detections > 0:
                    print("Tespit edilen nesneler çiziliyor...")
                    image_with_detections = draw_detections(image, results, model)

                    print("Ekranın ortasına en yakın nesne bulunuyor...")
                    closest_center = get_closest_detection_center(image, results, model)

                    if closest_center:
                        print(f"Fare {closest_center} koordinatlarına hareket ettiriliyor...")
                        move_mouse(closest_center[0], closest_center[1])

                        print("Fare tıklanıyor...")
                        click_mouse()

                        window.text_break_event.clear()
                        text_break(text_break_time)
                        window.text_break_event.set()

                        if window.checkBox.isChecked():
                            auto_pickup()

                        # Sayaç artırılıyor ve etiket güncelleniyor
                        window.killed_stones_count += 1
                        window.killed_stones_label.setText(str(window.killed_stones_count))
                    else:
                        print("Ekranın ortasına yakın nesne bulunamadı.")

                check_and_rotate_screen(results, model)

            except Exception as e:
                print(f"Hata: {e}")

            if window.checkBox_3.isChecked() and window.text_break_event.is_set():
                success = capture_captcha_and_solve(window.window_title, capture_window_by_pid, move_mouse, click_mouse)
                if not success:
                    print("CAPTCHA bulunamadı, normal işleme devam ediliyor...")

            # Revive kontrolü - Captcha kontrolünden sonra
            auto_revive(image, skill_keys=window.skill_keys)

            # Activate skills periodically based on Interval Time
            current_time = time.time()
            if window.checkBox_2.isChecked() and (current_time - last_skill_activation_time >= window.skill_activation_interval):
                activate_skills(window.pause_event, window.text_break_event, window.skill_keys)
                last_skill_activation_time = current_time

            time.sleep(captcha_check_interval)

    window.main_thread = threading.Thread(target=main_loop)
    window.main_thread.start()
    window.stop_event = stop_event

def stop_functionality(window):
    print("Stopping functionality...")
    if hasattr(window, 'main_thread') and window.main_thread and window.main_thread.is_alive():
        window.stop_event.set()
        window.main_thread.join(timeout=10)  # İş parçacığının durması için maksimum 10 saniye bekleyin
        if window.main_thread.is_alive():
            print("İş parçacığı durdurulamadı, zorla sonlandırılıyor.")
            window.main_thread = None  # İş parçacığını referanssız bırakın
        window.pause_event.clear()
        print("Döngü durduruldu.")
    else:
        print("Döngü zaten çalışmıyor.")