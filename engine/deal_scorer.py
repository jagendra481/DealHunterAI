from engine.comparator import DealResult


class DealScorer:

    @staticmethod
    def calculate(result: DealResult):

        score = 0

        if result.is_price_drop:
            score += 30

        if result.percentage >= 10:
            score += 20

        if result.percentage >= 20:
            score += 20

        if result.difference >= 1000:
            score += 15

        if result.difference >= 5000:
            score += 15

        return min(score, 100)
