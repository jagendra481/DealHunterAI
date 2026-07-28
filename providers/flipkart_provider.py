import re
import json
import random
import requests
from bs4 import BeautifulSoup

from database.models import Product
from utils.logger import logger


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
]


class FlipkartProvider:
    """100% Free Direct HTML & JSON-LD Flipkart Product Scraper"""

    def fetch_product(self, product):
        url = product.get("product_url") if isinstance(product, dict) else getattr(product, "product_url", "")
        if not url:
            return product

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.flipkart.com/"
        }

        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code != 200:
                logger.warning(f"Flipkart response status: {res.status_code}")
                return product

            soup = BeautifulSoup(res.text, "html.parser")
            
            title = ""
            price = 0.0
            image = ""
            rating = 4.3
            reviews = 0
            availability = "In Stock"

            # 1. Try JSON-LD Schema Extraction
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
                        
                        aggregate_rating = data.get("aggregateRating", {})
                        if isinstance(aggregate_rating, dict):
                            if aggregate_rating.get("ratingValue"):
                                rating = float(aggregate_rating["ratingValue"])
                            if aggregate_rating.get("reviewCount"):
                                reviews = int(aggregate_rating["reviewCount"])
                except Exception:
                    pass

            # 2. Fallback CSS Selectors for Title
            if not title:
                title_elem = soup.select_one("span.VU-453, h1._6ERy96, span.B_NuTv, h1._2xm1JU, ._35Kyg6, span.title")
                if title_elem:
                    title = title_elem.text.strip()

            # 3. Fallback CSS Selectors for Price
            if price <= 0:
                price_elem = soup.select_one(".Nx9bqj._4b5DiR, div._30jeq3, div._16JgA4, ._30jeq3._16JgA4, .yRaB8Z, div._25b18c div")
                if price_elem:
                    raw_price = re.sub(r"[^\d.]", "", price_elem.text.strip())
                    if raw_price:
                        price = float(raw_price)

            # 4. Fallback CSS Selectors for Image
            if not image:
                img_elem = soup.select_one("img.DLiA2n, img._396cs4, img._2r_T1I, img._396cs4._16JgA4, img._1b2f_6")
                if img_elem:
                    image = img_elem.get("src") or img_elem.get("data-src") or ""

            # Check Availability
            page_text = soup.text.lower()
            if any(term in page_text for term in ["out of stock", "sold out", "currently unavailable"]):
                availability = "Out of Stock"

            # Fallback title if empty
            if not title:
                title = product.get("name") if isinstance(product, dict) else getattr(product, "name", "Flipkart Product")

            # Fallback price if unparsed
            if price <= 0:
                old_p = product.get("current_price") if isinstance(product, dict) else getattr(product, "current_price", 0.0)
                price = float(old_p or 0.0)

            # Fallback image if empty
            if not image:
                image = product.get("image") if isinstance(product, dict) else getattr(product, "image", "")

            from urllib.parse import quote
            from config.settings import EARNKARO_ID

            aff_url = f"https://topurl.in/c/{EARNKARO_ID}?url={quote(url)}" if EARNKARO_ID else url

            # Construct standardized Product object
            result_product = Product(
                user_id=product.get("user_id", 0) if isinstance(product, dict) else getattr(product, "user_id", 0),
                name=title,
                product_url=url,
                affiliate_url=aff_url,
                asin=re.search(r"/p/([a-zA-Z0-9]+)", url).group(1) if re.search(r"/p/([a-zA-Z0-9]+)", url) else "",
                current_price=price,
                previous_price=product.get("current_price", 0.0) if isinstance(product, dict) else getattr(product, "current_price", 0.0),
                lowest_price=price,
                highest_price=price,
                source="flipkart",
                image=image,
                rating=rating,
                reviews=reviews,
                availability=availability,
                prime=False
            )


            logger.info(f"[Flipkart Scraper Success] '{title[:35]}...' -> Rs. {price:,.2f}")
            return result_product

        except Exception as err:
            logger.error(f"[Flipkart Scraper Error] {err}")
            return product
