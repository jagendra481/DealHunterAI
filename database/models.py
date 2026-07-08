from dataclasses import dataclass


@dataclass
class Product:

    name: str

    product_url: str

    affiliate_url: str

    asin: str

    current_price: float

    previous_price: float = 0

    lowest_price: float = 0

    highest_price: float = 0

    source: str = ""

    # New fields
    image: str = ""

    rating: float = 0.0

    reviews: int = 0

    availability: str = ""

    prime: bool = False

    last_checked: str = ""
