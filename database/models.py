from dataclasses import dataclass


@dataclass
class Product:

    user_id: int = 0

    name: str = ""

    product_url: str = ""

    affiliate_url: str = ""

    asin: str = ""

    current_price: float = 0.0

    previous_price: float = 0.0

    lowest_price: float = 0.0

    highest_price: float = 0.0

    source: str = ""

    image: str = ""

    rating: float = 0.0

    reviews: int = 0

    availability: str = ""

    prime: bool = False

    last_checked: str = ""
