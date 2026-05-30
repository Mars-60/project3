import time

from backend.collectors.window_logger import (
    get_window_info,
    has_window_changed
)

from backend.database.db import (
    initialize_database,
    insert_activity
)

from backend.utils.time_utils import (
    get_current_timestamp
)

initialize_database()

try:
    while True:

        app_name, window_title = get_window_info()

        if window_title and has_window_changed(
            app_name,
            window_title
        ):

            timestamp = get_current_timestamp()

            insert_activity(
                timestamp,
                app_name,
                window_title,
                "window_logger"
            )

            print(
                f"[{timestamp}] "
                f"{app_name} -> {window_title}"
            )

        time.sleep(1)

except KeyboardInterrupt:
    print("\nLogger stopped by user.")

except Exception as e:
    print("Error:", e)