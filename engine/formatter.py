class DealFormatter:

    @staticmethod
    def format(product, old_price, score):

        savings = old_price - product.current_price

        message = f"""
🔥 <b>DEAL ALERT</b> 🔥

📱 <b>{product.name}</b>

💰 Old Price: ₹{old_price}

💵 New Price: ₹{product.current_price}

💸 You Save: ₹{savings}

⭐ Deal Score: {score}/100

🏪 {product.source}

🛒 Buy Now:
{product.url}

#DealHunterAI
"""

        return message.strip()
