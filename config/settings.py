import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
RAINFOREST_API_KEY = os.getenv("RAINFOREST_API_KEY")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN not found in .env")

if CHAT_ID is None:
    raise ValueError("CHAT_ID not found in .env")

if RAINFOREST_API_KEY is None:
    raise ValueError("RAINFOREST_API_KEY not found in .env")

DATABASE_NAME = "products.db"
DATABASE_PATH = os.path.join("data", DATABASE_NAME)
# Scheduler
CHECK_INTERVAL_MINUTES = 60
