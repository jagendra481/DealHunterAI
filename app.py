import requests
from config.config import BOT_TOKEN, CHAT_ID

message = """
🚀 Hello Everyone!

My Telegram bot is working successfully! ✅
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print(response.text)
