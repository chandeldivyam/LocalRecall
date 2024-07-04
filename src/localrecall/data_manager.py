import os
import json
from datetime import datetime
from .utils import ensure_dir

class DataManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.join(os.getcwd(), 'data')
        ensure_dir(self.base_dir)

    def save_activity(self, screenshot_path, active_window, user_apps):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        activity_dir = os.path.join(self.base_dir, timestamp)
        ensure_dir(activity_dir)

        # Move screenshot to activity directory
        new_screenshot_path = os.path.join(activity_dir, os.path.basename(screenshot_path))
        os.rename(screenshot_path, new_screenshot_path)

        # Save activity data
        data = {
            "timestamp": timestamp,
            "screenshot": new_screenshot_path,
            "active_window": active_window,
            "user_apps": user_apps,
            "processed": False
        }

        with open(os.path.join(activity_dir, 'activity.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_unprocessed_activities(self):
        activities = []
        for entry in os.scandir(self.base_dir):
            if entry.is_dir():
                json_path = os.path.join(entry.path, 'activity.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if not data.get('processed', False):
                            activities.append(data)
        return activities

    def mark_activity_as_processed(self, timestamp):
        activity_dir = os.path.join(self.base_dir, timestamp)
        json_path = os.path.join(activity_dir, 'activity.json')
        if os.path.exists(json_path):
            with open(json_path, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data['processed'] = True
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()