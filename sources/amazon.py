from database.models import Product
from sources.base_source import BaseSource


class AmazonSource(BaseSource):

    def get_product(self, url):

        return Product(
            name="Sample Amazon Product",
            url=url,
            current_price=59999,
            previous_price=64999,
            lowest_price=54999,
            highest_price=69999,
            source="Amazon"
        )
