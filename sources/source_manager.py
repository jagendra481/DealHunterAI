from sources.amazon import AmazonSource
from sources.flipkart import FlipkartSource


class SourceManager:

    @staticmethod
    def get_source(url: str):

        url = url.lower()

        if any(domain in url for domain in ["amazon.", "amzn."]):
            return AmazonSource()

        if "flipkart" in url:
            return FlipkartSource()

        raise ValueError(f"Unsupported website: {url}")
