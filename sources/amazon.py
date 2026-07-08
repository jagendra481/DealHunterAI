from sources.base_source import BaseSource
from database.models import Product


class AmazonSource(BaseSource):

    def fetch_product(self, product):

        return Product(
            name=product["name"],
            url=product["url"],
            current_price=50000,          # Fake price for now
            previous_price=product["previous_price"],
            lowest_price=product["lowest_price"],
            highest_price=product["highest_price"],
            source=product["source"],
            last_checked=product["last_checked"]
        )
