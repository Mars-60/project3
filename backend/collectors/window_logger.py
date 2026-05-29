import pygetwindow as gw

last_window_title = None
def get_active_window():
    window = gw.getActiveWindow()

    if window is None:
        return None

    return window.title