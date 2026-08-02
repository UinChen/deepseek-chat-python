import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

BASE_URL = "https://api.deepseek.com"

MODEL = "deepseek-v4-flash"
if not API_KEY:
    raise ValueError("请配置 DEEPSEEK_API_KEY")