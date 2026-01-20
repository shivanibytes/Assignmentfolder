import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Base URL of the website we are scraping
BASE_URL = "https://books.toscrape.com/"


# get response (raw data) from given url 

def fetch_html_page_data(target_url):
    """
    Fetch HTML content of a webpage.
    This function sends a GET request to the given URL
    and returns the RAW page HTML if successful.
    """
    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()  
        # Automatically throws error for bad responses 404, 500 etc.
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return None


#take raw html page data and 
def parse_books_data(html):
    """
    Parse HTML content and extract book details.
    Extracts:
    - Title
    - Price
    - Availability
    - Rating
    """
    #lxml is fast and efficient HTML parser.
    soup = BeautifulSoup(html, "lxml")
    # Each book is inside <article class="product_pod">
    books = soup.select("article.product_pod")

    all_data = []
    for book in books:
        try:
            # Each book is inside <article class="product_pod">
            book_title = book.h3.a["title"]

            # Extract book price
            book_price = book.select_one("p.price_color").text.strip().replace("Â","")

            # Extract availability text (e.g., In stock)
            book_availability = book.select_one("p.availability").text.strip()
            
            # Extract rating is present as a class name  (it's bonus part of task)
            book_rating = book.select_one("p.star-rating")["class"][1]
            
            # Store extracted data in dictionary
            all_data.append({
                "Title": book_title,
                "Price": book_price,
                "Availability": book_availability,
                "Rating": book_rating
            })
        except Exception as e:
            # Skip book if any parsing issue occurs
            print(f"Skipping book due to parsing issue: {e}")
    return all_data


def save_data_into_file(data, filename):
    """
    Save scraped data into a file using pandas.
    Supported formats:
    - CSV  -> .csv
    - JSON -> .json
    """
    df = pd.DataFrame(data)

    # if file extenstion is .csv
    if filename.endswith(".csv"):
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"Data saved as CSV: {filename}")


    # if file extenstion is .json
    elif filename.endswith(".json"):
        df.to_json(filename, index=False, force_ascii=False)
        print(f"Data saved as JSON: {filename}")

    else:
        raise ValueError("Unsupported file format. Use .csv or .json")


def scrape_books(pages=None):
    """
    Main scraping controller function.
    Parameters:
    - pages (int): Number of pages to scrape
    - pages = None: Scrape all available pages
    """
    all_books_data = []
    page_count = 0
    target_url = BASE_URL
    # Start from base URL
    
    while True:
        page_count += 1
        print(f"Scraping page {page_count}")

        # Fetch HTML of current page
        html = fetch_html_page_data(target_url)
        if not html:
            break

        # Parse and collect book data
        all_books_data.extend(parse_books_data(html))
    
        soup = BeautifulSoup(html, "lxml")
        next_btn = soup.select_one("li.next a")

        # Stop loop if no next page found
        if not next_btn:
            print("No more pages available loop break here.")
            break

        # Stop loop if page limit is reached 
        if pages is not None and page_count >= pages:
            print(f"Reached page limit: {pages}, loop break here")
            break

        # Used to safely generate next page URLs during pagination.
        target_url = urljoin(target_url, next_btn["href"])
        print("BASE_URL::",target_url)

    # Save all scraped data into CSV
    save_data_into_file(all_books_data, "books.csv")

    # Save all scraped data into JSON
    save_data_into_file(all_books_data, "books.json")

    print(f"Total books scraped: {len(all_books_data)}")


if __name__ == "__main__":
    # Scrape first 5 pages only
    scrape_books(5)

    # Uncomment below line to scrape all pages if I pass none it extract all pages
    # scrape_books()