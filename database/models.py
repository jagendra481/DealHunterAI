from dataclasses import dataclass


@dataclass
class Product:

    name: str

    url: str

    current_price: float

    previous_price: float = 0

    lowest_price: float = 0

    highest_price: float = 0

    source: str = ""

    affiliate_url: str = ""

    asin: str = ""

    last_checked: str = ""
