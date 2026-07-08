from sources.base_source import BaseSource
from providers.amazon_provider import AmazonProvider


class AmazonSource(BaseSource):

    def fetch_product(self, product):

        print(f"🌐 Fetching Live Amazon Data: {product['name']}")

        live_product = AmazonProvider.get_product(
            product["product_url"]
        )

        # Preserve database values
        live_product.previous_price = product["previous_price"]
        live_product.lowest_price = product["lowest_price"]
        live_product.highest_price = product["highest_price"]
        live_product.last_checked = product["last_checked"]
        live_product.source = product["source"]

        return live_product
