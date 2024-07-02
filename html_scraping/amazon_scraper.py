from datetime import datetime
import requests
import csv
from bs4 import BeautifulSoup  # type: ignore
import concurrent.futures
from tqdm import tqdm # type: ignore
import time
import random

# Define user agent for the request headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.5',
}
NO_THREADS = 10

def get_page_html(url):
    """Fetch the HTML content of the page."""
    try:
        res = requests.get(url=url, headers=REQUEST_HEADER)
        res.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        return res.content
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def get_product_price(soup):
    """Extract the product price from the soup object."""
    try:
        price_span = soup.find("span", attrs={'class': "a-size-base a-color-price"})
        if price_span:
            price = price_span.text.strip().replace('$', '').replace(',', '')
            return float(price)
        else:
            print("Price not found")
    except (AttributeError, ValueError) as e:
        print(f"Error parsing price: {e}")
    return None

def get_product_title(soup):
    """Extract the product title from the soup object."""
    try:
        product_title = soup.find('span', id='productTitle')
        return product_title.text.strip() if product_title else "Title not found"
    except AttributeError as e:
        print(f"Error parsing title: {e}")
        return "Title not found"

def get_product_rating(soup):
    """Extract the product rating from the soup object."""
    try:
        product_rating_section = soup.find('i', attrs={'class': 'a-icon-star'})
        if product_rating_section:
            rating_text = product_rating_section.text.strip().split()[0]
            return float(rating_text.replace(',', '.'))
        else:
            print("Rating not found")
            return None
    except (AttributeError, ValueError) as e:
        print(f"Error parsing rating: {e}")
        return None

def get_product_info_details(soup):
    """Extract additional product details from the soup object."""
    details = {}
    try:
        info_details_section = soup.find('div', id='prodDetails')
        if info_details_section:
            data_tables = info_details_section.findAll('table', class_='prodetTable')
            for table in data_tables:
                table_rows = table.findAll('tr')
                for row in table_rows:
                    key = row.find('th').text.strip()
                    value = row.find('td').text.strip().replace('\n200e', '')
                    details[key] = value
        else:
            print("Product details section not found")
    except AttributeError as e:
        print(f"Error parsing product details: {e}")
    return details

def extract_product_info(url, output):
    """Extract all product information from the given URL."""
    product_info = {}
    # print(f"Scraping URL: {url}")
    html = get_page_html(url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        product_info["price"] = get_product_price(soup)
        product_info["title"] = get_product_title(soup)
        product_info["rating"] = get_product_rating(soup)
        product_info.update(get_product_info_details(soup))
    output.append(product_info)

if __name__ == "__main__":
    product_data = []
    urls = []
    with open("amazon_products_urls.csv", newline="") as csvfile:
        urls = list(csv.reader(csvfile, delimiter=","))
    with concurrent.futures.ThreadPoolExecutor(max_workers= NO_THREADS) as Executor:
        for wnk in range(len(urls)):
            if urls[wnk] and len(urls[wnk]) > 0:  # Check if the sublist is not empty
                Executor.submit(extract_product_info, urls[wnk][0], product_data)
            else:
             print(f"No URL found for index {wnk}")
    output_file_name ='output-{}.csv'.format(
        datetime.today().strftime("%m-%d-%Y"))
    with open(output_file_name, "w") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(product_data[0].keys())
        for product in product_data:
            writer.writerow(product.values())


# Use this to pause between requests
time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds

           

   