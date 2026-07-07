class PriceComparator:

    @staticmethod
    def compare(old_price, new_price):

        if old_price is None:
            return "NEW"

        if new_price < old_price:
            return "DROP"

        if new_price > old_price:
            return "INCREASE"

        return "SAME"
