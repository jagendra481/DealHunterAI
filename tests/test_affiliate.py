from services.affiliate_service import AffiliateService

url = input("Amazon URL: ")

print()
print(AffiliateService.generate_amazon_link(url))
