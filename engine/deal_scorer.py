class DealScorer:

    @staticmethod
    def calculate(old_price, new_price):

        if old_price <= 0:
            return 0

        drop = old_price - new_price

        if drop <= 0:
            return 0

        percentage = (drop / old_price) * 100

        if percentage >= 50:
            return 100

        elif percentage >= 40:
            return 90

        elif percentage >= 30:
            return 80

        elif percentage >= 20:
            return 70

        elif percentage >= 10:
            return 60

        elif percentage >= 5:
            return 40

        elif percentage >= 2:
            return 20

        return 10
