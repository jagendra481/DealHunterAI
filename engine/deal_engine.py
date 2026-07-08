from engine.product_service import ProductService
from sources.source_manager import SourceManager
from engine.price_comparator import PriceComparator
from engine.deal_scorer import DealScorer
from engine.formatter import DealFormatter
from services.telegram_service import TelegramService
import traceback


class DealEngine:

    def __init__(self):
        self.product_service = ProductService()

    def run(self):

        print("\n========== DEAL ENGINE ==========\n")

        products = self.product_service.get_all_products()

        print("\n" + "=" * 60)
        print("TOTAL PRODUCTS:", len(products))

        for p in products:
            print(f"• {p['name']}")

        print("=" * 60 + "\n")

        if not products:
            print("No Products Found")
            self.product_service.close()
            return

        for product in products:

            try:

                print(f"Checking: {product['name']}")

                # Detect Source
                source = SourceManager.get_source(
                    product["product_url"]
                )

                # Fetch latest LIVE data
                latest_product = source.fetch_product(product)

                # Compare prices
                status = PriceComparator.compare(
                    product["current_price"],
                    latest_product.current_price
                )

                # Calculate deal score
                score = DealScorer.calculate(
                    product["current_price"],
                    latest_product.current_price
                )

                print("--------------------------------------")
                print("Product      :", latest_product.name)
                print("Old Price    :", product["current_price"])
                print("New Price    :", latest_product.current_price)
                print("Status       :", status)
                print("Deal Score   :", score)
                print("--------------------------------------")

                if status == "DROP":

                    latest_product.previous_price = product["current_price"]

                    latest_product.lowest_price = min(
                        product["lowest_price"],
                        latest_product.current_price
                    )

                    latest_product.highest_price = max(
                        product["highest_price"],
                        latest_product.current_price
                    )

                    latest_product.last_checked = "NOW"

                    self.product_service.update_product(latest_product)

                    print("✅ Database Updated")

                    if score >= 60:

                        message = DealFormatter.format(
                            latest_product,
                            product["current_price"],
                            score
                        )

                        TelegramService.send_photo(
                            latest_product,
                            product["current_price"],
                            score
                        )

                        print("✅ Telegram Notification Sent")

                    else:
                        print("⚠️ Deal Score too low.")

                elif status == "SAME":

                    print("ℹ️ Price unchanged.")

                else:

                    print("📈 Price increased.")

            except Exception:

                print(f"\n❌ Error checking {product['name']}")
                traceback.print_exc()

        self.product_service.close()
