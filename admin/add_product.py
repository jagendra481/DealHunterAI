from database.models import Product
from engine.product_service import ProductService
from providers.amazon_provider import AmazonProvider
from services.affiliate_service import AffiliateService


def add_product():

    print("\n==============================")
    print("     ADD NEW PRODUCT")
    print("==============================\n")

    product_url = input("Paste Amazon Product URL : ").strip()

    try:

        print("\n🔍 Fetching Product Details...\n")

        # Fetch LIVE product
        product = AmazonProvider.get_product(product_url)

        # Generate Affiliate Link
        product.affiliate_url = AffiliateService.generate_amazon_link(
            product.product_url
        )

        print("✅ Product Found")
        print("--------------------------------")
        print("Name  :", product.name)
        print("Price :", product.current_price)
        print("ASIN  :", product.asin)
        print("--------------------------------")

        service = ProductService()

        service.add_product(product)

        service.close()

        print("\n✅ Product Added Successfully")

    except Exception as e:

        print("\n❌ Failed to Add Product")
        print(e)
