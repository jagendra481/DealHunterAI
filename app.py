from sources.source_manager import SourceManager

url = "https://www.amazon.in/test"

source = SourceManager.get_source(url)

product = source.fetch_product(url)

print(product)
