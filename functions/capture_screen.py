import numpy as np
import cv2
import win32gui
import win32ui
import win32con
import win32process

def get_hwnd_by_pid(pid):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    if not hwnds:
        print(f"Pencere bulunamadı: {pid}")
    return hwnds[0] if hwnds else None

def get_window_rect_by_pid(pid):
    hwnd = get_hwnd_by_pid(pid)
    if not hwnd:
        raise Exception(f"Pencere bulunamadı: {pid}")
    rect = win32gui.GetWindowRect(hwnd)
    return rect

def capture_window_by_pid(pid):
    hwnd = get_hwnd_by_pid(pid)
    if not hwnd:
        raise Exception(f"Pencere bulunamadı: {pid}")
    
    left, top, right, bottom = get_window_rect_by_pid(pid)
    width = right - left
    height = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    signedIntsArray = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    win32gui.DeleteObject(saveBitMap.GetHandle())

    img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    return img_bgr