from providers.amazon_provider import AmazonProvider

url = input("Amazon Product URL: ")

product = AmazonProvider.get_product(url)

print()

print("Product :", product.name)
print("Price   :", product.current_price)
print("ASIN    :", product.asin)
