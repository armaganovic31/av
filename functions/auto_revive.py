import cv2
import numpy as np
import time
from pynput.keyboard import Key, Controller
from functions.mouse_events import move_mouse, click_mouse

# İki farklı revive template'lerinin yolları burada belirleniyor
template_paths = ["revive_template_en.png", "revive_template_tr.png"]

keyboard = Controller()

def find_template_in_image(image, template_path, threshold=0.8):
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)  # Renkli formatta oku
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    if loc[0].size > 0 and loc[1].size > 0:
        return loc[1][0], loc[0][0], template  # İlk eşleşmeyi döner ve template'i döner
    return None, None, None

def click_at_position(x, y):
    move_mouse(x, y)
    time.sleep(1)
    click_mouse()
    time.sleep(0.5)

def activate_skills_and_mount(skill_keys):
    """
    Skilleri açmak ve binekten inip tekrar binmek için belirli tuş kombinasyonlarını kullanır.
    """
    print("Skiller açılıyor ve binekten inilip tekrar biniliyor...")

    # Skill tuşları
    for key in skill_keys:
        if key:  # Boş veya geçersiz tuşları atla
            try:
                keyboard.press(key)
                time.sleep(0.1)
                keyboard.release(key)
                time.sleep(1)  # Kısa bir bekleme süresi
            except ValueError as e:
                print(f"Geçersiz tuş: {key} - Hata: {e}")
            time.sleep(1)

    # CTRL + G tuş kombinasyonu
    keyboard.press(Key.ctrl)
    keyboard.press('g')
    time.sleep(0.1)
    keyboard.release('g')
    keyboard.release(Key.ctrl)
    time.sleep(1)

    print("Skiller açıldı ve binekten inilip tekrar binildi.")

def auto_revive(image, offset_x=0, offset_y=0, skill_keys=None):
    for template_path in template_paths:
        x, y, template = find_template_in_image(image, template_path)
        if x is not None and y is not None:
            # Tam ortasına ve 1px sağa götür
            x_center = x + offset_x + template.shape[1] // 2 + 1
            y_center = y + offset_y + template.shape[0] // 2
            click_at_position(x_center, y_center)
            print(f"Restart button clicked using template {template_path}.")
            if skill_keys:
                activate_skills_and_mount(skill_keys)
            return
    print("Restart button not found with any template.")