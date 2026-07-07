import os
import sqlite3

from config.settings import DATABASE_PATH
from utils.logger import logger


class Database:

    def __init__(self):

        os.makedirs("data", exist_ok=True)

        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.create_tables()

        logger.info("Database Connected")

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            url TEXT UNIQUE NOT NULL,

            current_price REAL NOT NULL,

            previous_price REAL DEFAULT 0,

            lowest_price REAL DEFAULT 0,

            highest_price REAL DEFAULT 0,

            source TEXT,

            active INTEGER DEFAULT 1,

            last_checked TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.connection.commit()

    def add_product(self, product):

        self.cursor.execute("""

        INSERT OR IGNORE INTO products(

            name,
            url,
            current_price,
            previous_price,
            lowest_price,
            highest_price,
            source,
            active,
            last_checked

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """, (

            product.name,
            product.url,
            product.current_price,
            product.previous_price,
            product.lowest_price,
            product.highest_price,
            product.source,
            1,
            product.last_checked

        ))

        self.connection.commit()

    def get_all_products(self):

        self.cursor.execute("""

        SELECT *

        FROM products

        WHERE active = 1

        """)

        return self.cursor.fetchall()

    def close(self):

        self.connection.close()
