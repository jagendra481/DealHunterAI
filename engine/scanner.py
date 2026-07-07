from engine.comparator import PriceComparator
from engine.deal_filter import DealFilter
from engine.formatter import TelegramFormatter

from utils.logger import logger


class Scanner:

    def process(self, old_product, new_product):

        logger.info(f"Checking: {new_product.name}")

        result = PriceComparator.compare(
            old_product.current_price,
            new_product.current_price
        )

        if DealFilter.should_post(result):

            message = TelegramFormatter.format(new_product)

            return message

        return None
