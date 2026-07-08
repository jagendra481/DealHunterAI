import re
import requests


class AmazonHelper:

    @staticmethod
    def expand_url(url: str) -> str:
        """
        Expands short Amazon URLs like amzn.in
        into the final Amazon product URL.
        """

        response = requests.get(
            url,
            allow_redirects=True,
            timeout=10
        )

        return response.url

    @staticmethod
    def extract_asin(url: str) -> str:
        """
        Extract ASIN from Amazon URL.
        """

        patterns = [

            r"/dp/([A-Z0-9]{10})",

            r"/gp/product/([A-Z0-9]{10})",

            r"/product/([A-Z0-9]{10})",

        ]

        for pattern in patterns:

            match = re.search(pattern, url)

            if match:
                return match.group(1)

        raise ValueError("ASIN not found")
