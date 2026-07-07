from engine.product_service import ProductService


class DealEngine:

    def __init__(self):
        self.product_service = ProductService()

    def run(self):

        print("\n========== DEAL ENGINE ==========\n")

        products = self.product_service.get_all_products()

        print(f"Products Found : {len(products)}\n")

        if not products:
            print("No products available.")
            return

        for product in products:

            print("------------------------------")
            print("Name   :", product["name"])
            print("Price  :", product["current_price"])
            print("Source :", product["source"])
            print("------------------------------")

        self.product_service.close()
