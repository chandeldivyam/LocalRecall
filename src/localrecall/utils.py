import os
from dotenv import load_dotenv

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_env_variables():
    """Load environment variables from .env file in the root directory."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dotenv_path = os.path.join(root_dir, '.env')
    load_dotenv(dotenv_path)

    # Set GEMINI_API_KEY as an environment variable
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        os.environ['GEMINI_API_KEY'] = gemini_api_key
    else:
        print("Warning: GEMINI_API_KEY not found in .env file")
    encryption_password = os.getenv('ENCRYPTION_PASSWORD')
    if encryption_password:
        os.environ['ENCRYPTION_PASSWORD'] = encryption_password
    else:
        print("Warning: ENCRYPTION_PASSWORD not found in .env file, setting the password to default")
        os.environ['ENCRYPTION_PASSWORD'] = "default"
