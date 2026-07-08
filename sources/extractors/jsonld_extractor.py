import json
from bs4 import BeautifulSoup


class JsonLDExtractor:

    @staticmethod
    def extract(html):

        soup = BeautifulSoup(html, "html.parser")

        scripts = soup.find_all(
            "script",
            type="application/ld+json"
        )

        for script in scripts:

            try:

                data = json.loads(script.string)

                if isinstance(data, list):

                    for item in data:

                        if item.get("@type") == "Product":
                            return item

                elif isinstance(data, dict):

                    if data.get("@type") == "Product":
                        return data

            except Exception:
                continue

        return None
