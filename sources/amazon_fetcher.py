import requests
from bs4 import BeautifulSoup

from utils.browser import HEADERS


class AmazonFetcher:

    @staticmethod
    def fetch(url):

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print("Status:", response.status_code)

        soup = BeautifulSoup(response.text, "lxml")

        print("TITLE:", soup.title.text)

        print("=" * 80)

        print(soup.prettify()[:3000])
