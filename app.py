from database.models import Product
from engine.scanner import Scanner

old_product = Product(
    name="Samsung Galaxy S25",
    url="https://amazon.in/test",
    current_price=79999,
    source="Amazon"
)

new_product = Product(
    name="Samsung Galaxy S25",
    url="https://amazon.in/test",
    current_price=69999,
    source="Amazon"
)

scanner = Scanner()

message = scanner.process(
    old_product,
    new_product
)

print(message)
