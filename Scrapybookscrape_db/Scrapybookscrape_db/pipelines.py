#For SQLITE database store
import sqlite3


class SQLitePipeline:
    def open_spider(self, spider):
        # Connect to SQLite database (creates file if not exists)
        self.connection = sqlite3.connect("books.db")
        self.cursor = self.connection.cursor()

        # Create table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT,
                availability TEXT,
                rating TEXT
            )
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        # Insert data into table
        self.cursor.execute("""
            INSERT INTO books (title, price, availability, rating)
            VALUES (?, ?, ?, ?)
        """, (
            item["Title"],
            item["Price"],
            item["Availability"],
            item["Rating"]
        ))

        self.connection.commit()   #saves the row into db
        return item

    def close_spider(self, spider):   #spider finishes crawling
        self.connection.close()
