from sources.amazon import AmazonSource
from sources.flipkart import FlipkartSource
from providers.generic_store_provider import GenericStoreProvider


class GenericSourceWrapper:
    def fetch_product(self, product):
        return GenericStoreProvider.fetch_product(product)


class SourceManager:

    @staticmethod
    def get_source(url: str):
        url = url.lower()

        if any(domain in url for domain in ["amazon.", "amzn."]):
            return AmazonSource()

        if any(domain in url for domain in ["flipkart.", "fkrt."]):
            return FlipkartSource()

        if any(domain in url for domain in ["myntra", "meesho", "ajio", "reliancedigital", "reliance", "croma", "nykaa", "tatacliq"]):
            return GenericSourceWrapper()

        return GenericSourceWrapper()

