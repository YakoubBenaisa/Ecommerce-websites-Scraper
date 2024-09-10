

import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, time

def hard_job(url, sheet):
    # URL and headers
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    # Fetch the data
    response = requests.get(url, headers=headers)

    # Prepare data variables
    title = curr_price = was_price = save = promo = img_url = ean = 'N/A'
    drop = 'N/A'

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract data
        title = soup.find('span', attrs={"data-test": "product-title"}).text
        curr_price = soup.find("li", attrs={"data-test": "product-price-primary"})['content']
        img = soup.find("div", attrs={"class": "MediaGallerystyles__ImageWrapper-sc-1jwueuh-3"})
        img_url = img.find('source')['srcset'] if img else 'N/A'

        try:
            was_price = soup.find("span", attrs={"data-test": "price-was"}).text
        except AttributeError:
            was_price = 'N/A'

        try:
            promo = soup.find("span", attrs={"data-test": "price-save"}).text
        except AttributeError:
            promo = '0'

        if was_price != 'N/A':
            try:
                int_was_pr = float(was_price[5:])
                promo = f"{int_was_pr - float(curr_price):.2f}"
                drop = f"{100 - float(curr_price) * 100 / int_was_pr:.2f}"
            except ValueError:
                drop = 'N/A'
                promo = 'N/A'

        desc = soup.find("div", attrs={"class": "product-description-content-text"})
        if desc:
            lis = desc.find_all('li')
            for li in lis:
                if li.text.startswith("EAN"):
                    ean = li.text[5:]

        # Print the data (optional)
        #

        # Append data to Google Sheets
        sheet.append_row([title, url, img_url, ean.replace(".",""), curr_price, was_price, drop, promo])
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        #

def main():
    # Google Sheets credentials and setup
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('web-scraper-py-4ff549cd04d5.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by ID
    sheet_id = '1cOVDv7D5j1i2puwNmTps7lkmJB9ZRzCcFVtpWbCQQFE'
    sheet = client.open_by_key(sheet_id).sheet1

    # Check if header exists and add if not
    existing_headers = sheet.row_values(1)
    expected_headers = ['Name', 'URL', 'Image URL', 'EAN', 'Now Price', 'Was Price', 'Price Drop', 'Promotion']

    #if existing_headers != expected_headers:
     #   sheet.append_row(expected_headers)

    # Read URLs from file and process them
    with open('product_links.txt', 'r') as f:
        i = 0
        for l in f.readlines():
            try:
                hard_job(l.strip(), sheet)
            except:
                time.sleep(5)
                continue
                

            i += 1
            print(f"Processed {i} URLs")
            time.sleep(1)

if __name__ == "__main__":
    main()
