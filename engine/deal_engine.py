from engine.product_service import ProductService
from engine.price_comparator import PriceComparator
from engine.deal_scorer import DealScorer


class DealEngine:

    def __init__(self):
        self.product_service = ProductService()

    def run(self):

        print("\n========== DEAL ENGINE ==========\n")

        products = self.product_service.get_all_products()

        if not products:
            print("No Products Found")
            return

        for product in products:

            old_price = product["current_price"]

            # Temporary simulation
            new_price = old_price - 5000

            status = PriceComparator.compare(
                old_price,
                new_price
            )

            score = DealScorer.calculate(
                old_price,
                new_price
            )

            print("-----------------------------")
            print("Product :", product["name"])
            print("Old Price :", old_price)
            print("New Price :", new_price)
            print("Status :", status)
            print("Deal Score :", score)
            print("-----------------------------")
