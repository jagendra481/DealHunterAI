from database.models import Product
from engine.product_service import ProductService
from services.affiliate_service import AffiliateService
from utils.amazon_helper import AmazonHelper


def add_product():

    print("\nADD NEW PRODUCT\n")

    name = input("Product Name : ").strip()

    product_url = input("Product URL : ").strip()

    current_price = float(input("Current Price : "))

    source = input("Source (Amazon/Flipkart): ").strip()

    # Generate affiliate link
    affiliate_url = AffiliateService.generate_amazon_link(product_url)

    # Extract ASIN only for Amazon
    asin = ""

    if "amazon" in product_url or "amzn" in product_url:
        try:
            expanded = AmazonHelper.expand_url(product_url)
            asin = AmazonHelper.extract_asin(expanded)
        except Exception:
            print("⚠️ Could not extract ASIN.")

    product = Product(
        name=name,
        product_url=product_url,
        affiliate_url=affiliate_url,
        asin=asin,
        current_price=current_price,
        previous_price=current_price,
        lowest_price=current_price,
        highest_price=current_price,
        source=source,
        last_checked=""
    )

    service = ProductService()

    service.add_product(product)

    service.close()

    print("\n✅ Product Added Successfully")
