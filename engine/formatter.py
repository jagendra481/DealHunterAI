from database.models import Product


class TelegramFormatter:

    @staticmethod
    def format(product):

        return f"""
🔥 <b>PRICE DROP ALERT</b>

📦 <b>{product.name}</b>

💰 Price: ₹{product.current_price}

🏪 Store: {product.source}

🔗 {product.url}
"""
