from urllib.parse import urlparse, parse_qs, urlencode


class AffiliateService:

    ASSOCIATE_TAG = "jagendra4810f-21"

    @classmethod
    def generate_amazon_link(cls, url: str):

        parsed = urlparse(url)

        query = parse_qs(parsed.query)

        query["tag"] = [cls.ASSOCIATE_TAG]

        new_query = urlencode(query, doseq=True)

        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
