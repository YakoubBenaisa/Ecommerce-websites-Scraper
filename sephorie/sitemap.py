import requests, time, json
from bs4 import BeautifulSoup


url = 'https://www.sephora.co.uk/sephora_https_products_sitemap-www-gb.xml'
    
    # URL and headers
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,fr-FR;q=0.7,en-GB;q=0.6,ar;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
        'Sec-CH-UA': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    
# Fetch the data
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raise HTTPError for bad responses
discount = "/"

# Parse the HTML content
soup = BeautifulSoup(response.content, 'xml')

# Extract data
urls = soup.find_all('loc')

with open("sephori_urls.txt", "w") as pen:
    for url in urls:
        if (url.text).startswith("https"):
            pen.write(url.text+"\n")