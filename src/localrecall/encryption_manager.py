import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import tempfile
from .utils import load_env_variables

class EncryptionManager:
    def __init__(self, password=os.environ.get('ENCRYPTION_PASSWORD'), salt_file='encryption_salt.bin'):
        if not password:
            load_env_variables()
            password = os.environ.get('ENCRYPTION_PASSWORD')
        if not password:
            raise ValueError("ENCRYPTION_PASSWORD environment variable is not set.")

        self.salt_file = salt_file
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as file:
                salt = file.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as file:
                file.write(salt)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)

    def encrypt_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                data = file.read()
            encrypted_data = self.fernet.encrypt(data)
            with open(file_path + '.encrypted', 'wb') as file:
                file.write(encrypted_data)
            os.remove(file_path)
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {str(e)}")

    def decrypt_file(self, encrypted_file_path, decrypted_file_path=None):
        try:
            with open(encrypted_file_path, 'rb') as file:
                encrypted_data = file.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            if not decrypted_file_path:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    decrypted_file_path = temp_file.name
            
            with open(decrypted_file_path, 'wb') as file:
                file.write(decrypted_data)
            
            return decrypted_file_path
        except InvalidToken:
            raise ValueError("Decryption failed: Invalid token. The encryption key may be incorrect or the data may be corrupted.")
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {str(e)}")

    def encrypt_string(self, text):
        return self.fernet.encrypt(text.encode()).decode()

    def decrypt_string(self, encrypted_text):
        try:
            return self.fernet.decrypt(encrypted_text.encode()).decode()
        except InvalidToken:
            raise ValueError("Decryption failed: Invalid token. The encryption key may be incorrect or the data may be corrupted.")
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {str(e)}")
