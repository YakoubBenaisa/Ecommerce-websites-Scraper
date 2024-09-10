import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, time

def hard_s(url, sheet):
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
        'Sec-Fetch-User': '?1'
    }

    try:
        # Fetch the data
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract data
        name = soup.find('input', attrs={'name':'productName'})['value']
        image_div = soup.find('div', class_='productpage-image')
        image = image_div.find('img')['src'].strip()
        try:
            ean_code = soup.find('input', attrs={'name': 'mf'})['data-flix-ean'] 
        except:
            ean_code = "N/A"
        
        now_price = soup.find('span', attrs={'class': 'Price'}).text.strip()
        try:
            was_price = soup.find('span', class_='rrp').text.strip()
        except:
            was_price = "N/A"

        discount = "N/A"
        if was_price != "N/A":
            nwp = now_price.replace('£', '')
            wsp = was_price.replace('£', '')
            try:
                discount = f"{100 - float(nwp) * 100 / float(wsp):.2f} %"
            except ValueError:
                discount = "N/A"

        promo_span = soup.find('span', attrs={'class': 'Price-details'})
        promotions = promo_span.findChildren('span') if promo_span else []
        
        promotion = "N/A"
            
        for promo in promotions:
            if 'rrp' not in promo.get('class', []):
                promotion = promo.text.strip()
                break
	  
        # Prepare data for Google Sheets
        data = [name, url, image, ean_code, now_price, was_price, discount, promotion]
        
        # Append data to Google Sheets
        sheet.append_row(data)
        print(f"Added data for URL: {url}")

    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")

def main():
    # Google Sheets credentials and setup
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('web-scraper-py-4ff549cd04d5.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by ID
    sheet_id = ''
    sheet = client.open_by_key(sheet_id).get_worksheet(2)  # Get the third sheet

    # Check if header exists and add if not
    existing_headers = sheet.row_values(1)
    expected_headers = ['Name', 'URL', 'Image URL', 'EAN', 'Now Price', 'Was Price', 'Price Drop', 'Promotion']
    
    #if existing_headers != expected_headers:
    #    sheet.insert_row(expected_headers, 1)

    # Read URLs from file and process them
    with open('sephori_urls.txt', 'r') as f:
        for i, line in enumerate(f):
            url = line.strip()
            try:
                hard_s(url, sheet)
            except Exception as e:
                print(f"Failed to process URL {url}: {e}")
                time.sleep(5)
                continue

            print(f"Processed {i + 1} URLs")
            time.sleep(1)

if __name__ == "__main__":
    main()
