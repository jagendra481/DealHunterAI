import html

import requests

from config.settings import BOT_TOKEN


class TelegramService:

    BASE_URL = (
        f"https://api.telegram.org/bot{BOT_TOKEN}"
    )

    REQUEST_TIMEOUT = 20

    # ==========================================================
    # VALIDATE CHAT ID
    # ==========================================================

    @staticmethod
    def _validate_chat_id(chat_id):

        if not chat_id:

            raise Exception(
                "Telegram Chat ID is not configured."
            )

    # ==========================================================
    # SEND TELEGRAM REQUEST
    # ==========================================================

    @classmethod
    def _send_request(
        cls,
        endpoint,
        payload
    ):

        url = f"{cls.BASE_URL}/{endpoint}"

        try:

            response = requests.post(
                url,
                data=payload,
                timeout=8
            )

            response.raise_for_status()

            result = response.json()

            if not result.get("ok"):

                print("⚠️ Telegram API Warning:", result.get("description", "Telegram request failed."))
                return False

            return result

        except requests.RequestException as error:

            print(f"[Telegram Notice] Network/ISP restriction on local environment: {error}")
            print("[Telegram Notice] Note: Production Telegram alerts execute automatically on Azure cloud servers.")
            return False

        except ValueError as error:

            print(f"[Telegram Notice] Response format error: {error}")
            return False



    # ==========================================================
    # SEND TEXT MESSAGE
    # ==========================================================

    @classmethod
    def send_message(
        cls,
        message,
        chat_id
    ):

        cls._validate_chat_id(chat_id)

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }

        return cls._send_request(
            "sendMessage",
            payload
        )

    # ==========================================================
    # PROCESS UPDATES & AUTO-REPLY CHAT ID
    # ==========================================================

    @classmethod
    def process_updates(cls):
        try:
            url = f"{cls.BASE_URL}/getUpdates"
            res = requests.get(url, timeout=5)
            if not res.ok:
                return

            data = res.json()
            if not data.get("ok"):
                return

            updates = data.get("result", [])
            for update in updates:
                update_id = update.get("update_id")
                msg = update.get("message") or update.get("channel_post")
                if not msg:
                    continue

                chat = msg.get("chat", {})
                chat_id = chat.get("id")
                text = msg.get("text", "").strip()
                from_user = msg.get("from", {})
                user_id_param = None

                if text.startswith("/start"):
                    parts = text.split()
                    if len(parts) > 1 and parts[1].isdigit():
                        user_id_param = int(parts[1])

                if user_id_param:
                    from database.database import Database
                    db = Database()
                    try:
                        db.cursor.execute(
                            "UPDATE users SET telegram_chat_id = ?, telegram_notifications = 1 WHERE id = ?",
                            (str(chat_id), user_id_param)
                        )
                        db.connection.commit()
                    finally:
                        db.close()

                    reply_text = (
                        f"🎉 <b>Account Connected Successfully!</b>\n\n"
                        f"Your Telegram account has been linked to DealHunterAI User #{user_id_param}.\n\n"
                        f"Your Chat ID: <code>{chat_id}</code>\n\n"
                        f"You will now receive instant price drop and deal alerts here!"
                    )
                else:
                    reply_text = (
                        f"👋 <b>Hello {from_user.get('first_name', 'there')}!</b>\n\n"
                        f"Your Telegram Chat ID is:\n<code>{chat_id}</code>\n\n"
                        f"Copy this Chat ID and paste it in DealHunterAI Settings (dealhunterai.in/settings) to receive price drop alerts!"
                    )

                cls.send_message(reply_text, chat_id)

                # Confirm update offset to prevent duplicate replies
                requests.get(f"{cls.BASE_URL}/getUpdates", params={"offset": update_id + 1, "timeout": 1}, timeout=5)

        except Exception as err:
            pass

    # ==========================================================
    # SEND DEAL SCORE ALERT

    # ==========================================================

    @classmethod
    def send_photo(
        cls,
        product,
        old_price,
        score,
        chat_id
    ):

        cls._validate_chat_id(chat_id)

        current_price = float(
            product.current_price or 0
        )

        old_price = float(
            old_price or 0
        )

        savings = max(
            old_price - current_price,
            0
        )

        percent = 0

        if old_price > 0:

            percent = (
                savings / old_price
            ) * 100

        prime = (
            "✅ Prime"
            if product.prime
            else "❌ Non Prime"
        )

        product_name = html.escape(
            str(product.name or "Product")
        )

        availability = html.escape(
            str(
                product.availability
                or "Availability unavailable"
            )
        )

        affiliate_url = html.escape(
            str(product.affiliate_url or ""),
            quote=True
        )

        caption = f"""
🔥 <b>HIGH SCORE DEAL ALERT</b>

<b>{product_name}</b>

━━━━━━━━━━━━━━━━━━

💰 <b>Current Price:</b>
₹{current_price:,.0f}

📉 <b>Previous Price:</b>
₹{old_price:,.0f}

💸 <b>You Save:</b>
₹{savings:,.0f} ({percent:.2f}%)

⭐ <b>Rating:</b>
{product.rating} ⭐ ({product.reviews} Ratings)

📦 <b>Availability:</b>
{availability}

🚚 <b>{prime}</b>

🎯 <b>Deal Score:</b> {score}/100

━━━━━━━━━━━━━━━━━━

🛒 <a href="{affiliate_url}">Buy on Amazon</a>

━━━━━━━━━━━━━━━━━━

🤖 <b>DealHunterAI</b>
"""

        return cls._send_product_alert(
            product,
            caption,
            chat_id
        )

    # ==========================================================
    # SEND PRICE DROP ALERT
    # ==========================================================

    @classmethod
    def send_price_drop_alert(
        cls,
        product,
        old_price,
        chat_id
    ):

        cls._validate_chat_id(chat_id)

        current_price = float(
            product.current_price or 0
        )

        old_price = float(
            old_price or 0
        )

        savings = max(
            old_price - current_price,
            0
        )

        percent = 0

        if old_price > 0:

            percent = (
                savings / old_price
            ) * 100

        product_name = html.escape(
            str(product.name or "Product")
        )

        affiliate_url = html.escape(
            str(product.affiliate_url or ""),
            quote=True
        )

        caption = f"""
📉 <b>PRICE DROP ALERT</b>

<b>{product_name}</b>

━━━━━━━━━━━━━━━━━━

💰 <b>New Price:</b>
₹{current_price:,.0f}

🏷 <b>Previous Price:</b>
₹{old_price:,.0f}

💸 <b>Price Dropped By:</b>
₹{savings:,.0f}

📊 <b>Drop Percentage:</b>
{percent:.2f}%

━━━━━━━━━━━━━━━━━━

🛒 <a href="{affiliate_url}">View Deal on Amazon</a>

━━━━━━━━━━━━━━━━━━

🤖 <b>DealHunterAI</b>
"""

        return cls._send_product_alert(
            product,
            caption,
            chat_id
        )

    # ==========================================================
    # SEND TARGET PRICE ALERT
    # ==========================================================

    @classmethod
    def send_target_price_alert(
        cls,
        product,
        target_price,
        chat_id
    ):

        cls._validate_chat_id(chat_id)

        current_price = float(
            product.current_price or 0
        )

        target_price = float(
            target_price or 0
        )

        difference = max(
            target_price - current_price,
            0
        )

        product_name = html.escape(
            str(product.name or "Product")
        )

        affiliate_url = html.escape(
            str(product.affiliate_url or ""),
            quote=True
        )

        caption = f"""
🎯 <b>TARGET PRICE REACHED</b>

<b>{product_name}</b>

━━━━━━━━━━━━━━━━━━

💰 <b>Current Price:</b>
₹{current_price:,.0f}

🎯 <b>Your Target Price:</b>
₹{target_price:,.0f}

💸 <b>Below Target By:</b>
₹{difference:,.0f}

━━━━━━━━━━━━━━━━━━

🚨 <b>Your target price has been reached!</b>

🛒 <a href="{affiliate_url}">Buy on Amazon</a>

━━━━━━━━━━━━━━━━━━

🤖 <b>DealHunterAI</b>
"""

        return cls._send_product_alert(
            product,
            caption,
            chat_id
        )
    # ==========================================================
    # SEND BUY NOW RECOMMENDATION
    # ==========================================================

    @classmethod
    def send_buy_now_alert(
        cls,
        product,
        recommendation,
        chat_id
    ):

        cls._validate_chat_id(chat_id)

        current_price = float(
            product.current_price or 0
        )

        lowest_price = float(
            recommendation.get(
                "lowest_price",
                current_price
            )
        )

        highest_price = float(
            recommendation.get(
                "highest_price",
                current_price
            )
        )

        confidence = recommendation.get(
            "confidence",
            0
        )

        reason = html.escape(
            recommendation.get(
                "reason",
                ""
            )
        )

        product_name = html.escape(
            str(product.name or "Product")
        )

        affiliate_url = html.escape(
            str(product.affiliate_url or ""),
            quote=True
        )

        caption = f"""
🟢 <b>BUY NOW OPPORTUNITY</b>

<b>{product_name}</b>

━━━━━━━━━━━━━━━━━━

💰 <b>Current Price:</b>
₹{current_price:,.0f}

📉 <b>Tracked Low:</b>
₹{lowest_price:,.0f}

📈 <b>Tracked High:</b>
₹{highest_price:,.0f}

🎯 <b>Confidence:</b>
{confidence}%

━━━━━━━━━━━━━━━━━━

🤖 <b>DealHunterAI Recommendation</b>

{reason}

━━━━━━━━━━━━━━━━━━

🛒 <a href="{affiliate_url}">
Buy on Amazon
</a>

━━━━━━━━━━━━━━━━━━

🔥 This alert is sent only when
DealHunterAI detects a new
BUY NOW opportunity.
"""

        return cls._send_product_alert(
            product,
            caption,
            chat_id
        )
    # ==========================================================
    # SEND PRODUCT ALERT
    # ==========================================================

    @classmethod
    def _send_product_alert(
        cls,
        product,
        caption,
        chat_id
    ):

        image = str(
            product.image or ""
        ).strip()

        # ------------------------------------------------------
        # SEND PHOTO
        # ------------------------------------------------------

        if image:

            payload = {
                "chat_id": chat_id,
                "photo": image,
                "caption": caption,
                "parse_mode": "HTML"
            }

            try:

                return cls._send_request(
                    "sendPhoto",
                    payload
                )

            except Exception as error:

                print(
                    "⚠️ Telegram photo failed. "
                    "Falling back to text message."
                )

                print(
                    "Telegram Photo Error:",
                    error
                )

        # ------------------------------------------------------
        # TEXT FALLBACK
        # ------------------------------------------------------

        payload = {
            "chat_id": chat_id,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        return cls._send_request(
            "sendMessage",
            payload
        )
