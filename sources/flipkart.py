from providers.flipkart_provider import FlipkartProvider
from sources.base_source import BaseSource


class FlipkartSource(BaseSource):

    def __init__(self):
        self.provider = FlipkartProvider()

    def fetch_product(self, product):
        return self.provider.fetch_product(product)

