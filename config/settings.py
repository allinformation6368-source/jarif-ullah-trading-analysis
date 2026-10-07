import os
from dotenv import load_dotenv

load_dotenv()

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
