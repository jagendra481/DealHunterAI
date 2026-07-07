import os
import sqlite3

from config.settings import DATABASE_PATH
from utils.logger import logger


class Database:

    def __init__(self):
        os.makedirs("data", exist_ok=True)

        self.connection = sqlite3.connect(DATABASE_PATH)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

        logger.info("Database Connected.")

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                url TEXT UNIQUE NOT NULL,

                current_price REAL,

                previous_price REAL,

                lowest_price REAL,

                highest_price REAL,

                source TEXT,

                last_checked TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        """)

        self.connection.commit()

        logger.info("Products table created.")

    def add_product(self, product):
        self.cursor.execute("""
            INSERT OR IGNORE INTO products (
                name,
                url,
                current_price,
                previous_price,
                lowest_price,
                highest_price,
                source,
                last_checked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.name,
            product.url,
            product.current_price,
            product.previous_price,
            product.lowest_price,
            product.highest_price,
            product.source,
            product.last_checked
        ))

        self.connection.commit()

        logger.info(f"Product Added: {product.name}")

    def get_product(self, url):
        self.cursor.execute(
            "SELECT * FROM products WHERE url = ?",
            (url,)
        )

        return self.cursor.fetchone()

    def get_all_products(self):
        self.cursor.execute(
            "SELECT * FROM products"
        )

        return self.cursor.fetchall()

    def update_product(self, product):
        self.cursor.execute("""
            UPDATE products
            SET

                current_price = ?,
                previous_price = ?,
                lowest_price = ?,
                highest_price = ?,
                last_checked = ?

            WHERE url = ?
        """, (
            product.current_price,
            product.previous_price,
            product.lowest_price,
            product.highest_price,
            product.last_checked,
            product.url
        ))

        self.connection.commit()

        logger.info(f"Updated Product: {product.name}")

    def delete_product(self, url):
        self.cursor.execute(
            "DELETE FROM products WHERE url = ?",
            (url,)
        )

        self.connection.commit()

        logger.info("Product Deleted")

    def close(self):
        self.connection.close()

        logger.info("Database Closed.")
