import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN not found in .env")

if CHAT_ID is None:
    raise ValueError("CHAT_ID not found in .env")

DATABASE_NAME = "products.db"
DATABASE_PATH = os.path.join("data", DATABASE_NAME)
