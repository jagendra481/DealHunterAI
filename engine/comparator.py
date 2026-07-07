from dataclasses import dataclass


@dataclass
class DealResult:
    old_price: float
    new_price: float
    difference: float
    percentage: float
    is_price_drop: bool


class PriceComparator:

    @staticmethod
    def compare(old_price: float, new_price: float):

        if old_price <= 0:
            raise ValueError("Old price must be greater than zero.")

        difference = old_price - new_price

        percentage = (difference / old_price) * 100

        return DealResult(
            old_price=old_price,
            new_price=new_price,
            difference=round(difference, 2),
            percentage=round(percentage, 2),
            is_price_drop=new_price < old_price
        )
