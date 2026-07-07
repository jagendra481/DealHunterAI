from database.models import Product
from sources.base_source import BaseSource


class AmazonSource(BaseSource):

    def fetch_product(self, url):

        return Product(
            name="Samsung Galaxy S25",
            url=url,
            current_price=69999,
            previous_price=74999,
            lowest_price=68999,
            highest_price=79999,
            source="Amazon"
        )
