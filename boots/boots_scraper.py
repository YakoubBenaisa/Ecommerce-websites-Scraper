import requests
from bs4 import BeautifulSoup
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

def clean_price(price_str):
    """Remove non-numeric characters and convert to float."""
    cleaned_str = re.sub(r'[^\d.,]', '', price_str).replace(',', '')
    try:
        return float(cleaned_str)
    except ValueError:
        return None

def hard_job(url, sheet):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find Elements
        try:
            name = soup.find("div", attrs={'id': 'estore_product_title'}).find('h1').text.strip()
        except AttributeError:
            name = "N/A"

        try:
            imgID = soup.find("input", attrs={"id": "s7viewerAsset"})['value']
            imgURL = "https://boots.scene7.com/is/image/" + imgID
        except (AttributeError, KeyError):
            imgURL = "N/A"

        try:
            productID = soup.find('div', attrs={'class': 'productid'}).text.strip()
        except AttributeError:
            productID = "N/A"

        try:
            Now_Price = soup.find('div', attrs={'id': 'PDP_productPrice'}).text.strip()
        except AttributeError:
            Now_Price = "N/A"

        try:
            Was_Price_str = soup.find('div', attrs={"class": "was_price was_price_redesign"}).text.strip()
            Was_Price_value = clean_price(Was_Price_str)
        except AttributeError:
            Was_Price_str = "N/A"
            Was_Price_value = None

        try:
            Price_DC_str = soup.find('div', attrs={'class': 'saving saving_redesign'}).text.strip()
            Price_DC_value = clean_price(Price_DC_str)
            if Was_Price_value is not None and Price_DC_value is not None:
                Price_Drop = f"{(Price_DC_value * 100 / Was_Price_value):.2f}%"
            else:
                Price_Drop = "N/A"
        except AttributeError:
            Price_Drop = "N/A"
            Price_DC_value = None

        try:
            Promotions_tag = soup.find('ul', attrs={'class': 'pdp-promotion-redesign-container'})
            promotionsA = Promotions_tag.find_all("a")
            promotions = [promotion.text.strip() for promotion in promotionsA]
        except AttributeError:
            promotions = ["N/A"]

      
        # Append data to the second sheet
        sheet.append_row([name, url, imgURL, productID, Now_Price, Was_Price_str, Price_Drop, ', '.join(promotions)])

    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")

def main():
    # Google Sheets credentials and setup
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('web-scraper-py-4ff549cd04d5.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by ID
    sheet_id = ''
    sheet = client.open_by_key(sheet_id).get_worksheet(1)  # Access the second sheet (index 1)

    # Check if header exists and add if not
    expected_headers = ['Name', 'URL', 'Image URL', 'Product ID', 'Now Price', 'Was Price', 'Price Drop', 'Promotions']
    existing_headers = sheet.row_values(1)
    
   # if existing_headers != expected_headers:
       # sheet.insert_row(expected_headers, 1)

    # Read URLs from file and process them
    with open('urls.txt', 'r', encoding='utf-8') as f:
        i = 0
        for l in f.readlines():
            try:
                hard_job(l.strip(), sheet)
            except Exception as e:
                print(f"Error processing URL {l.strip()}: {e}")
                time.sleep(5)
                continue
                
            i += 1
            print(f"Processed {i} URLs")
            time.sleep(1)

if __name__ == "__main__":
    main()
