from database.models import Product
from sources.base_source import BaseSource


class FlipkartSource(BaseSource):

    def fetch_product(self, url):

        return Product(
            name="Nothing Phone 3",
            url=url,
            current_price=34999,
            previous_price=37999,
            lowest_price=33999,
            highest_price=39999,
            source="Flipkart"
        )
