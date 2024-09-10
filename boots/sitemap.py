import requests
from bs4 import BeautifulSoup

def scrape_save():
    url = 'https://www.boots.com/wcsstore/eBootsStorefrontAssetStore/sitemap/product-sitemap.xml'
    headers = {        
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Ensure we notice bad responses
    except requests.RequestException as e:
        print(f"Error fetching the XML file: {e}")
        return

    # Parse the XML content
    soup = BeautifulSoup(response.text, 'xml')
    urls = soup.find_all('loc')

    # Write URLs to a file with utf-8 encoding
    with open("urls.txt", "w", encoding="utf-8") as file:
        for url in urls:
            file.write(url.text + "\n")

if __name__ == "__main__":
    scrape_save()
