import requests

from config.settings import BOT_TOKEN, CHAT_ID


class TelegramService:

    BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

    @classmethod
    def send_message(cls, message):

        url = f"{cls.BASE_URL}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(url, data=payload)

        print("Telegram Message:", response.status_code)

    @classmethod
    def send_photo(cls, product, old_price, score):

        url = f"{cls.BASE_URL}/sendPhoto"

        savings = old_price - product.current_price

        percent = 0

        if old_price > 0:
            percent = (savings / old_price) * 100

        prime = "✅ Prime" if product.prime else "❌ Non Prime"

        caption = f"""
🔥 <b>DEAL ALERT</b>

<b>{product.name}</b>

━━━━━━━━━━━━━━━━━━

💰 <b>Current Price:</b>
₹{product.current_price:,.0f}

📉 <b>Previous Price:</b>
₹{old_price:,.0f}

💸 <b>You Save:</b>
₹{savings:,.0f} ({percent:.2f}%)

⭐ <b>Rating:</b>
{product.rating} ⭐ ({product.reviews} Ratings)

📦 <b>Availability:</b>
{product.availability}

🚚 <b>{prime}</b>

🎯 <b>Deal Score:</b> {score}/100

━━━━━━━━━━━━━━━━━━

🛒 <a href="{product.affiliate_url}">Buy on Amazon</a>

━━━━━━━━━━━━━━━━━━

🤖 <b>DealHunterAI</b>
"""

        payload = {
            "chat_id": CHAT_ID,
            "photo": product.image,
            "caption": caption,
            "parse_mode": "HTML"
        }

        response = requests.post(url, data=payload)

        print("Telegram Photo:", response.status_code)
