import pygetwindow as gw
import win32gui
import win32process
import psutil

last_window_info = None
def get_active_window():
    window = gw.getActiveWindow()

    if window is None:
        return None

    return window.title

def has_window_changed(app_name, window_title):
    global last_window_info

    current_info = (app_name, window_title)

    if current_info != last_window_info:
        last_window_info = current_info
        return True

    return False

def get_window_info():
    hwnd=win32gui.GetForegroundWindow()

    _,pid=win32process.GetWindowThreadProcessId(hwnd)

    process=psutil.Process(pid)

    app_name=process.name()
    window_title=win32gui.GetWindowText(hwnd)
    return app_name,window_title

