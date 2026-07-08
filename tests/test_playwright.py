from playwright.sync_api import sync_playwright


url = input("Enter Flipkart URL: ").strip()

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(url, wait_until="networkidle")

    print("\n========================")
    print("PAGE TITLE")
    print("========================\n")

    print(page.title())

    browser.close()
