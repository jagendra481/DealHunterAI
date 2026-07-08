from database.models import Product
from engine.product_service import ProductService
from services.affiliate_service import AffiliateService


def add_product():

    print("\nADD NEW PRODUCT\n")

    name = input("Product Name : ")

    url = input("Product URL : ")

    price = float(input("Current Price : "))

    source = input("Source (Amazon/Flipkart): ")

    affiliate_url = AffiliateService.generate_amazon_link(url)

    product = Product(
        name=name,
        url=affiliate_url,
        current_price=price,
        previous_price=price,
        lowest_price=price,
        highest_price=price,
        source=source
    )

    service = ProductService()

    service.add_product(product)

    service.close()

    print("\n✅ Product Added Successfully")
