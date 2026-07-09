from database.database import Database
from providers.amazon_provider import AmazonProvider


class ProductService:

    def __init__(self):
        self.db = Database()

    def add_product(self, product):
        self.db.add_product(product)

    def get_all_products(self):
        return self.db.get_all_products()

    def update_product(self, product):
        self.db.update_product(product)

    def update_metadata(self, product):
        self.db.update_metadata(product)

    def delete_product(self, product_id):
        self.db.delete_product(product_id)

    def get_product_by_asin(self, asin):
        return self.db.get_product_by_asin(asin)

    def get_product_by_id(self, product_id):
        return self.db.get_product_by_id(product_id)

    def refresh_product(self, product_id):

        # Get existing product
        existing = self.db.get_product_by_id(product_id)

        if existing is None:
            raise Exception("Product not found.")

        # Fetch latest data from Amazon
        latest = AmazonProvider.get_product(existing["product_url"])

        # Preserve existing information
        latest.product_url = existing["product_url"]
        latest.affiliate_url = existing["affiliate_url"]
        latest.previous_price = existing["current_price"]
        latest.lowest_price = min(
            existing["lowest_price"],
            latest.current_price
        )
        latest.highest_price = max(
            existing["highest_price"],
            latest.current_price
        )

        # Update metadata
        self.db.update_metadata(latest)

    def close(self):
        self.db.close()
