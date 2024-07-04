from .data_manager import DataManager
from .screenshot_capture import ScreenshotCapture
from .window_info import WindowInfo
import time

class ActivityTracker:
    def __init__(self, interval=30, save_dir=None, compress=False, compress_quality=85, resize_factor=1.0):
        self.interval = interval
        self.data_manager = DataManager(save_dir)
        self.screenshot_capture = ScreenshotCapture(compress, compress_quality, resize_factor)
        self.window_info = WindowInfo()

    def run(self):
        try:
            while True:
                screenshot_path = self.screenshot_capture.capture()
                active_window = self.window_info.get_active_window_info()
                user_apps = self.window_info.get_user_applications()
                
                self.data_manager.save_activity(screenshot_path, active_window, user_apps)
                
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("Activity tracking stopped.")

