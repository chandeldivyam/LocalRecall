import win32gui
import win32process
import psutil

class WindowInfo:
    @staticmethod
    def get_active_window_info():
        hwnd = win32gui.GetForegroundWindow()
        return WindowInfo.get_window_info(hwnd)

    @staticmethod
    def get_window_info(hwnd):
        if hwnd:
            try:
                title = win32gui.GetWindowText(hwnd)
            except Exception:
                title = "Unknown Title"
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                return {
                    "title": title,
                    "process_name": process.name(),
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                return {"title": title, "process_name": "Unknown"}
        return None

    @staticmethod
    def get_user_applications():
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                windows.append(hwnd)
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)
        return [WindowInfo.get_window_info(hwnd) for hwnd in windows if WindowInfo.get_window_info(hwnd)]