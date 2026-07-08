from utils.browser import Browser

url = input("Enter Flipkart Product URL: ").strip()

html = Browser.get_html(url)

print(html[:3000])
