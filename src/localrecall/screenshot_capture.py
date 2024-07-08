import mss
import mss.tools
from datetime import datetime
import os
from PIL import Image
from .utils import ensure_dir
from .encryption_manager import EncryptionManager

class ScreenshotCapture:
    def __init__(self, compress=False, compress_quality=85, resize_factor=1.0):
        self.sct = mss.mss()
        self.ss_dir = os.path.join(os.getcwd(), 'screenshots')
        ensure_dir(self.ss_dir)
        self.compress = compress
        self.compress_quality = compress_quality
        self.resize_factor = resize_factor
        self.encryption_manager = EncryptionManager()

    def capture(self):
        screenshot = self.sct.grab(self.sct.monitors[0])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.compress:
            filename = f"screenshot_{timestamp}.jpg"
            filepath = os.path.join(self.ss_dir, filename)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            if self.resize_factor != 1.0:
                new_size = tuple(int(dim * self.resize_factor) for dim in img.size)
                img = img.resize(new_size, Image.LANCZOS)
            
            img.save(filepath, format='JPEG', quality=self.compress_quality, optimize=True)
        else:
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.ss_dir, filename)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)

        # Encrypt the screenshot file
        self.encryption_manager.encrypt_file(filepath)
        encrypted_filepath = filepath + '.encrypted'

        # Remove the original unencrypted file
        if os.path.exists(filepath):
            os.remove(filepath)

        return encrypted_filepath