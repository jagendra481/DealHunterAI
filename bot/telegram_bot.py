import requests

from config.settings import BOT_TOKEN, CHAT_ID
from utils.logger import logger


class TelegramBot:

    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"

    def send_message(self, message):

        url = f"{self.base_url}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        try:
            response = requests.post(url, data=data)

            if response.status_code == 200:
                logger.info("Telegram message sent successfully.")
            else:
                logger.error(
                    f"Telegram Error: {response.status_code} | {response.text}"
                )

        except Exception as e:
            logger.error(f"Exception: {e}")
