import mss
import mss.tools
from datetime import datetime
import os
from PIL import Image
from .utils import ensure_dir

class ScreenshotCapture:
    def __init__(self, compress=False, compress_quality=85, resize_factor=1.0):
        self.sct = mss.mss()
        self.temp_dir = os.path.join(os.getcwd(), 'temp_screenshots')
        ensure_dir(self.temp_dir)
        self.compress = compress
        self.compress_quality = compress_quality
        self.resize_factor = resize_factor

    def capture(self):
        screenshot = self.sct.grab(self.sct.monitors[0])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.compress:
            filename = f"screenshot_{timestamp}.jpg"
            filepath = os.path.join(self.temp_dir, filename)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            if self.resize_factor != 1.0:
                new_size = tuple(int(dim * self.resize_factor) for dim in img.size)
                img = img.resize(new_size, Image.LANCZOS)
            
            img.save(filepath, format='JPEG', quality=self.compress_quality, optimize=True)
        else:
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.temp_dir, filename)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)

        return filepath