import scrapy


class BooksSpider(scrapy.Spider):
    """
    Scrapy spider to scrape book data from books.toscrape.com
    Extracts:
    - Title
    - Price
    - Availability
    - Rating
    """

    # Unique spider name (used while running the spider)
    name = "books"

    # Restrict spider to this domain only
    allowed_domains = ["books.toscrape.com"]

    # Starting URL (first page)
    start_urls = ["https://books.toscrape.com/"]

    # Pagination control
    # Set max_pages = None to scrape all pages
    # Set max_pages = 5 to scrape only first 5 pages
    max_pages = 5
    page_count = 1  # Tracks current page number

    def parse_data(self, response):
        """
        This method is called automatically by Scrapy for each page.
        It:
        1. Extracts book details from the current page
        2. Handles pagination and moves to the next page if required
        """

        # Loop through all book blocks on the page
        for book in response.css("article.product_pod"):
            try:
                # Extract book title
                book_title = book.css("h3 a::attr(title)").get()

                # Extract book price
                book_price = book.css("p.price_color::text").get().strip()

                # Extract availability text (cleaned using regex)
                book_availability = book.css(
                    "p.availability::text"
                ).re_first(r"\S.*\S")

                # Extract rating from class attribute
                rating_class = book.css("p.star-rating").attrib.get("class", "")
                book_rating = rating_class.replace("star-rating", "").strip()

                # Yield extracted data as dictionary send to pipeline without stoping loop
                yield {
                    "Title": book_title,
                    "Price": book_price,
                    "Availability": book_availability,
                    "Rating": book_rating,
                }

            except Exception as e:
                # Log warning if any book fails to parse
                self.logger.warning(f"Failed to parse a book: {e}")

        # -------- Pagination Logic --------

        # Get relative URL of next page
        next_page = response.css("li.next a::attr(href)").get()

        # Continue only if next page exists
        if next_page:
            # Check page limit (if set)
            if self.max_pages is None or self.page_count < self.max_pages:
                self.page_count += 1
                next_page_url = response.urljoin(next_page)

                # Send request to next page download it and send response to parse
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_data
                )
            else:
                self.logger.info(
                    f"Reached maximum page limit: {self.max_pages}"
                )
        else:
            self.logger.info("No more pages available. Scraping finished.")
