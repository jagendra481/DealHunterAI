from utils.browser import Browser

url = "https://books.toscrape.com/"

html = Browser.get_html(url)

print(html[:1000])
