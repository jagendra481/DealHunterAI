from engine.comparator import PriceComparator
from engine.deal_scorer import DealScorer

result = PriceComparator.compare(
    old_price=80000,
    new_price=68000
)

score = DealScorer.calculate(result)

print(result)
print(f"Deal Score = {score}/100")
