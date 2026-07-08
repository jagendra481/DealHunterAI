from utils.amazon_helper import AmazonHelper

url = input("Amazon URL: ")

expanded = AmazonHelper.expand_url(url)

print()

print("Expanded URL")
print(expanded)

print()

asin = AmazonHelper.extract_asin(expanded)

print("ASIN:", asin)
