from sources.amazon import AmazonSource
from sources.flipkart import FlipkartSource


class SourceManager:

    @staticmethod
    def get_source(url: str):

        url = url.lower()

        if "amazon" in url:
            return AmazonSource()

        if "flipkart" in url:
            return FlipkartSource()

        raise ValueError("Unsupported website")
