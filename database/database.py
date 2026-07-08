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

            asin TEXT,

            product_url TEXT UNIQUE NOT NULL,

            affiliate_url TEXT NOT NULL,

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

        # -------------------------------
        # Database Migration (v2)
        # -------------------------------

        columns = [

            ("image", "TEXT DEFAULT ''"),

            ("rating", "REAL DEFAULT 0"),

            ("reviews", "INTEGER DEFAULT 0"),

            ("availability", "TEXT DEFAULT ''"),

            ("prime", "INTEGER DEFAULT 0")

        ]

        for column_name, column_type in columns:

            try:

                self.cursor.execute(
                    f"ALTER TABLE products ADD COLUMN {column_name} {column_type}"
                )

            except sqlite3.OperationalError:
                # Column already exists
                pass

        self.connection.commit()

    def add_product(self, product):

        try:

            self.cursor.execute(
                """
                INSERT INTO products(

                    name,
                    asin,
                    product_url,
                    affiliate_url,
                    current_price,
                    previous_price,
                    lowest_price,
                    highest_price,
                    source,
                    image,
                    rating,
                    reviews,
                    availability,
                    prime,
                    active,
                    last_checked

                )

                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    product.name,
                    product.asin,
                    product.product_url,
                    product.affiliate_url,
                    product.current_price,
                    product.previous_price,
                    product.lowest_price,
                    product.highest_price,
                    product.source,
                    product.image,
                    product.rating,
                    product.reviews,
                    product.availability,
                    int(product.prime),
                    1,
                    product.last_checked
                )
            )

            self.connection.commit()

        except sqlite3.IntegrityError:
            raise Exception("This product is already being tracked.")

    def get_all_products(self):

        self.cursor.execute("""
            SELECT *
            FROM products
            WHERE active = 1
            ORDER BY id
        """)

        return self.cursor.fetchall()

    def get_product_by_asin(self, asin):

        self.cursor.execute(
            """
            SELECT *
            FROM products
            WHERE asin = ?
            """,
            (asin,)
        )

        return self.cursor.fetchone()

    def update_product(self, product):

        self.cursor.execute(
            """
            UPDATE products
            SET
                previous_price = ?,
                current_price = ?,
                lowest_price = ?,
                highest_price = ?,
                image = ?,
                rating = ?,
                reviews = ?,
                availability = ?,
                prime = ?,
                last_checked = ?
            WHERE product_url = ?
            """,
            (
                product.previous_price,
                product.current_price,
                product.lowest_price,
                product.highest_price,
                product.image,
                product.rating,
                product.reviews,
                product.availability,
                int(product.prime),
                product.last_checked,
                product.product_url
            )
        )

        self.connection.commit()

    def delete_product(self, product_id):

        self.cursor.execute(
            """
            DELETE FROM products
            WHERE id = ?
            """,
            (product_id,)
        )

        self.connection.commit()

    def close(self):

        self.connection.close()
