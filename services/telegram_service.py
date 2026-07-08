import requests

from config.settings import BOT_TOKEN, CHAT_ID


class TelegramService:

    @staticmethod
    def send_message(message):

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(url, data=payload)

        print("Telegram Status:", response.status_code)
