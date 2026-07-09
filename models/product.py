from dataclasses import dataclass


@dataclass
class Product:

    user_id: int = 0

    name: str = ""

    asin: str = ""

    product_url: str = ""

    affiliate_url: str = ""

    current_price: float = 0

    previous_price: float = 0

    lowest_price: float = 0

    highest_price: float = 0

    source: str = ""

    image: str = ""

    rating: float = 0

    reviews: int = 0

    availability: str = ""

    prime: bool = False

    last_checked: str = ""
