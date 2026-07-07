from fake_useragent import UserAgent

HEADERS = {
    "User-Agent": UserAgent().random,
    "Accept-Language": "en-IN,en;q=0.9"
}
