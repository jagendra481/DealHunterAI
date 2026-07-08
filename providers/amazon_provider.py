import requests

from config.settings import RAINFOREST_API_KEY
from database.models import Product
from utils.amazon_helper import AmazonHelper


class AmazonProvider:

    BASE_URL = "https://api.rainforestapi.com/request"

    @classmethod
    def get_product(cls, url):

        # Expand short Amazon URL
        expanded_url = AmazonHelper.expand_url(url)

        # Extract ASIN
        asin = AmazonHelper.extract_asin(expanded_url)

        params = {
            "api_key": RAINFOREST_API_KEY,
            "amazon_domain": "amazon.in",
            "asin": asin,
            "type": "product"
        }

        response = requests.get(
            cls.BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if "product" not in data:
            raise Exception("Product not found in Rainforest API response")

        product = data["product"]

        # ----------------------------
        # Get Current Price
        # ----------------------------

        price = None

        if product.get("buybox_winner"):
            buybox = product["buybox_winner"]

            if buybox.get("price"):
                price = float(buybox["price"]["value"])

        if price is None and product.get("buybox_price"):
            price = float(product["buybox_price"]["value"])

        if price is None and product.get("price"):
            price = float(product["price"]["value"])

        if price is None:
            raise Exception("Unable to fetch current product price.")

        # ----------------------------
        # Product Title
        # ----------------------------

        title = product.get("title", "Unknown Product")

        # ----------------------------
        # Return Product Object
        # ----------------------------

        return Product(
            name=title,
            product_url=url,
            affiliate_url=expanded_url,
            asin=asin,
            current_price=price,
            previous_price=0,
            lowest_price=price,
            highest_price=price,
            source="amazon",
            last_checked=""
        )
