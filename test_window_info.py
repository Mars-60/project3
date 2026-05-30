from backend.collectors.window_logger import get_window_info

app_name, window_title = get_window_info()

print("App:", app_name)
print("Title:", window_title)