from config.deal_rules import (
    MIN_PERCENTAGE_DROP,
    MIN_PRICE_DROP,
    MIN_PRODUCT_PRICE
)


class DealFilter:

    @staticmethod
    def should_post(result):

        if result.new_price < MIN_PRODUCT_PRICE:
            return False

        if result.difference < MIN_PRICE_DROP:
            return False

        if result.percentage < MIN_PERCENTAGE_DROP:
            return False

        return True
