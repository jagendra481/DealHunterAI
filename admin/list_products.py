from engine.product_service import ProductService


def list_products():

    service = ProductService()

    products = service.get_all_products()

    print()

    for product in products:

        print("-" * 50)

        print("ID :", product["id"])
        print("Name :", product["name"])
        print("Price :", product["current_price"])
        print("Source :", product["source"])

    service.close()
