import re
import requests
from bs4 import BeautifulSoup

from config.settings import RAINFOREST_API_KEY
from database.models import Product
from utils.amazon_helper import AmazonHelper


class AmazonScraper:
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    @classmethod
    def scrape_product(cls, asin, url, expanded_url):
        target_urls = [
            f"https://www.amazon.in/dp/{asin}?th=1&psc=1",
            f"https://www.amazon.in/gp/product/{asin}"
        ]

        for target_url in target_urls:
            for ua in cls.USER_AGENTS:
                headers = {
                    "User-Agent": ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Cache-Control": "max-age=0",
                    "Upgrade-Insecure-Requests": "1"
                }

                try:
                    res = requests.get(target_url, headers=headers, timeout=12)
                    if res.status_code != 200:
                        continue

                    soup = BeautifulSoup(res.text, "html.parser")
                    title_elem = soup.find(id="productTitle") or soup.find("h1")
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()

                    # Extract Price
                    price = None
                    price_whole = soup.select_one(".a-price-whole")
                    if price_whole:
                        raw_price = re.sub(r"[^\d.]", "", price_whole.text.replace(",", ""))
                        if raw_price:
                            try:
                                price = float(raw_price)
                            except ValueError:
                                pass

                    if price is None:
                        offscreen = soup.select_one(".a-price .a-offscreen, .apexPriceToPay .a-offscreen, #priceblock_ourprice, #priceblock_dealprice")
                        if offscreen:
                            raw_price = re.sub(r"[^\d.]", "", offscreen.text.replace(",", ""))
                            if raw_price:
                                try:
                                    price = float(raw_price)
                                except ValueError:
                                    pass

                    # Extract Image
                    image = ""
                    img_elem = soup.find(id="landingImage") or soup.find(id="main-image") or soup.select_one("img[data-old-hires]")
                    if img_elem:
                        image = img_elem.get("data-old-hires") or img_elem.get("src") or ""

                    # Extract Rating
                    rating = 0.0
                    rating_elem = soup.select_one("span.a-icon-alt, i.a-icon-star span")
                    if rating_elem:
                        match = re.search(r"(\d+(?:\.\d+)?)", rating_elem.text)
                        if match:
                            try:
                                rating = float(match.group(1))
                            except ValueError:
                                pass

                    # Extract Reviews
                    reviews = 0
                    reviews_elem = soup.find(id="acrCustomerReviewText")
                    if reviews_elem:
                        match = re.search(r"([\d,]+)", reviews_elem.text)
                        if match:
                            try:
                                reviews = int(match.group(1).replace(",", ""))
                            except ValueError:
                                pass

                    prime = bool(soup.select_one(".a-icon-prime, #primeBadge"))
                    availability = "In Stock" if "In stock" in res.text or not soup.find(id="outOfStock") else "Currently unavailable"

                    if title and price and price > 0:
                        print(f"[Amazon Scraper Success] '{title[:30]}...' -> Rs. {price:,.0f}")
                        from urllib.parse import quote
                        from config.settings import EARNKARO_ID, AMAZON_ASSOCIATE_TAG

                        if AMAZON_ASSOCIATE_TAG:
                            sep = "&" if "?" in expanded_url else "?"
                            aff_url = f"{expanded_url}{sep}tag={AMAZON_ASSOCIATE_TAG}"
                        elif EARNKARO_ID:
                            aff_url = f"https://topurl.in/c/{EARNKARO_ID}?url={quote(expanded_url)}"
                        else:
                            aff_url = expanded_url


                        return Product(
                            name=title,
                            product_url=url,
                            affiliate_url=aff_url,
                            asin=asin,
                            current_price=price,
                            previous_price=0,
                            lowest_price=price,
                            highest_price=price,
                            source="amazon",
                            image=image,
                            rating=rating,
                            reviews=reviews,
                            availability=availability,
                            prime=prime,
                            last_checked=""
                        )

                except Exception as err:
                    print(f"[Amazon Scraper Notice] Scraping attempt notice: {err}")

        return None



class AmazonProvider:
    BASE_URL = "https://api.rainforestapi.com/request"

    @classmethod
    def get_product(cls, url):
        expanded_url = AmazonHelper.expand_url(url)
        asin = AmazonHelper.extract_asin(expanded_url)

        # --------------------------------------------------
        # 1. DIRECT HTML SCRAPER (100% FREE & UNLIMITED)
        # --------------------------------------------------
        scraped_product = AmazonScraper.scrape_product(asin, url, expanded_url)
        if scraped_product:
            return scraped_product

        # --------------------------------------------------
        # 2. RAINFOREST API (FALLBACK IF KEY CONFIGURED)
        # --------------------------------------------------
        if not RAINFOREST_API_KEY:
            raise Exception("Direct HTML scraper couldn't fetch price and no Rainforest API key is set.")

        print("ℹ️ Direct HTML scraper fallback -> Requesting Rainforest API...")
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
            raise Exception("Product not found.")

        product = data["product"]

        price = None
        if product.get("buybox_winner") and product["buybox_winner"].get("price"):
            price = float(product["buybox_winner"]["price"]["value"])
        if price is None and product.get("buybox_price"):
            price = float(product["buybox_price"]["value"])
        if price is None and product.get("price"):
            price = float(product["price"]["value"])
        if price is None:
            raise Exception("Price not found.")

        image = ""
        if product.get("main_image"):
            if isinstance(product["main_image"], dict):
                image = product["main_image"].get("link", "")
            else:
                image = product["main_image"]

        rating = float(product.get("rating", 0))
        reviews = int(product.get("ratings_total", 0))

        availability = ""
        prime = False
        if product.get("buybox_winner"):
            availability = product["buybox_winner"].get("availability", {}).get("raw", "")
            prime = product["buybox_winner"].get("is_prime", False)

        return Product(
            name=product.get("title", "Unknown Product"),
            product_url=url,
            affiliate_url=expanded_url,
            asin=asin,
            current_price=price,
            previous_price=0,
            lowest_price=price,
            highest_price=price,
            source="amazon",
            image=image,
            rating=rating,
            reviews=reviews,
            availability=availability,
            prime=prime,
            last_checked=""
        )
