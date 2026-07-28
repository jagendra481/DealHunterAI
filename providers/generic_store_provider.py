import re
import json
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from database.models import Product
from config.settings import EARNKARO_ID
from utils.logger import logger


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
]


class GenericStoreProvider:
    """Multi-Store Scraper for Myntra, Meesho, Ajio, Reliance Digital & E-Commerce Platforms"""

    @classmethod
    def fetch_product(cls, product):
        url = product.get("product_url") if isinstance(product, dict) else getattr(product, "product_url", "")
        if not url:
            return product

        source_name = "online_store"
        url_lower = url.lower()
        if "myntra" in url_lower:
            source_name = "myntra"
        elif "meesho" in url_lower:
            source_name = "meesho"
        elif "ajio" in url_lower:
            source_name = "ajio"
        elif "reliancedigital" in url_lower or "reliance" in url_lower:
            source_name = "reliance_digital"

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            res = requests.get(url, headers=headers, timeout=12)
            soup = BeautifulSoup(res.text, "html.parser")

            title = ""
            price = 0.0
            image = ""
            rating = 4.2
            reviews = 12

            # 1. JSON-LD Schema
            ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in ld_scripts:
                if not script.string:
                    continue
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    if isinstance(data, dict) and (data.get("@type") == "Product" or "offers" in data):
                        if data.get("name"):
                            title = data["name"]
                        if data.get("image"):
                            img_val = data["image"]
                            image = img_val[0] if isinstance(img_val, list) else img_val

                        offers = data.get("offers", {})
                        if isinstance(offers, list):
                            offers = offers[0]
                        if isinstance(offers, dict) and offers.get("price"):
                            price = float(offers["price"])
                except Exception:
                    pass

            # 2. Fallback Title
            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.text.strip()
                elif soup.title:
                    title = soup.title.text.strip().split("|")[0].split("-")[0].strip()

            # 3. Fallback Price
            if price <= 0:
                price_elems = soup.find_all(text=re.compile(r"₹\s*[\d,]+"))
                for elem in price_elems:
                    raw = re.sub(r"[^\d.]", "", elem.text.strip())
                    if raw:
                        try:
                            val = float(raw)
                            if val > 50:
                                price = val
                                break
                        except ValueError:
                            pass

            # 4. Fallback Image
            if not image:
                meta_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
                if meta_img:
                    image = meta_img.get("content", "")

            # Construct EarnKaro Affiliate Link
            aff_url = f"https://topurl.in/c/{EARNKARO_ID}?url={quote(url)}" if EARNKARO_ID else url

            # Default Title / Price fallbacks
            if not title:
                title = f"{source_name.replace('_', ' ').title()} Product"
            if price <= 0:
                price = product.get("current_price", 999.0) if isinstance(product, dict) else getattr(product, "current_price", 999.0)
            if not image:
                image = product.get("image", "") if isinstance(product, dict) else getattr(product, "image", "")

            result_product = Product(
                user_id=product.get("user_id", 0) if isinstance(product, dict) else getattr(product, "user_id", 0),
                name=title,
                product_url=url,
                affiliate_url=aff_url,
                asin="",
                current_price=price,
                previous_price=product.get("current_price", price) if isinstance(product, dict) else getattr(product, "current_price", price),
                lowest_price=price,
                highest_price=price,
                source=source_name,
                image=image,
                rating=rating,
                reviews=reviews,
                availability="In Stock",
                prime=False
            )

            logger.info(f"[{source_name.upper()} Success] '{title[:35]}...' -> Rs. {price:,.2f}")
            return result_product

        except Exception as err:
            logger.error(f"[{source_name.upper()} Error] {err}")
            return product
