import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_URL = f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"