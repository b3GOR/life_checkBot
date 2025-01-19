import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('API')
API_NUTRITION = os.getenv('API_NUTRITION')