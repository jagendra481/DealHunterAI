import os
import sqlite3

from config.settings import DATABASE_PATH
from utils.logger import logger


class Database:

    def __init__(self):

        database_directory = os.path.dirname(
            DATABASE_PATH
        )

        if database_directory:

            os.makedirs(
                database_directory,
                exist_ok=True
            )

        else:

            os.makedirs(
                "data",
                exist_ok=True
            )

        self.connection = sqlite3.connect(
            DATABASE_PATH,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        self.cursor = self.connection.cursor()

        self.create_tables()

        logger.info("Database Connected")

    # ==========================================================
    # TABLE CREATION
    # ==========================================================

    def create_tables(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                email TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                telegram_chat_id TEXT DEFAULT '',

                telegram_notifications INTEGER DEFAULT 1,

                target_price_alerts INTEGER DEFAULT 1,

                deal_score_alerts INTEGER DEFAULT 1,

                price_drop_alerts INTEGER DEFAULT 1,

                auth_provider TEXT DEFAULT 'password',

                google_id TEXT DEFAULT '',

                is_admin INTEGER DEFAULT 0,

                is_active INTEGER DEFAULT 1,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_registrations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                otp_hash TEXT NOT NULL,
                otp_expires_at TIMESTAMP NOT NULL,
                otp_attempts INTEGER DEFAULT 0,
                last_otp_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                name TEXT NOT NULL,

                asin TEXT,

                product_url TEXT NOT NULL,

                affiliate_url TEXT DEFAULT '',

                current_price REAL DEFAULT 0,

                previous_price REAL DEFAULT 0,

                lowest_price REAL DEFAULT 0,

                highest_price REAL DEFAULT 0,

                source TEXT DEFAULT '',

                image TEXT DEFAULT '',

                rating REAL DEFAULT 0,

                reviews INTEGER DEFAULT 0,

                availability TEXT DEFAULT '',

                prime INTEGER DEFAULT 0,

                active INTEGER DEFAULT 1,

                target_price REAL DEFAULT 0,

                target_alert_sent INTEGER DEFAULT 0,

                last_recommendation TEXT DEFAULT '',

                recommendation_alert_sent INTEGER DEFAULT 0,

                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                UNIQUE(user_id, asin),

                UNIQUE(user_id, product_url)

            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                product_id INTEGER NOT NULL,

                price REAL NOT NULL,

                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE CASCADE

            )
            """
        )

        # ======================================================
        # SCAN RUNS
        # ======================================================

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_runs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                started_at TIMESTAMP NOT NULL,

                completed_at TIMESTAMP,

                status TEXT DEFAULT 'RUNNING',

                total_products INTEGER DEFAULT 0,

                checked_products INTEGER DEFAULT 0,

                failed_products INTEGER DEFAULT 0,

                duration_seconds REAL DEFAULT 0,

                error_message TEXT DEFAULT '',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
            """
        )

        # ======================================================
        # INDEXES
        # ======================================================

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_price_history_product_id
            ON price_history(product_id)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_scan_runs_started_at
            ON scan_runs(started_at)
            """
        )

        self.connection.commit()

        self._run_user_migrations()

        self._run_product_migrations()

    # ==========================================================
    # USER MIGRATIONS
    # ==========================================================

    def _run_user_migrations(self):

        columns = [
            ("telegram_notifications", "INTEGER DEFAULT 1"),
            ("target_price_alerts", "INTEGER DEFAULT 1"),
            ("deal_score_alerts", "INTEGER DEFAULT 1"),
            ("price_drop_alerts", "INTEGER DEFAULT 1"),
            ("auth_provider", "TEXT DEFAULT 'password'"),
            ("google_id", "TEXT DEFAULT ''")
        ]

        for column_name, column_type in columns:

            try:

                self.cursor.execute(
                    f"""
                    ALTER TABLE users
                    ADD COLUMN {column_name} {column_type}
                    """
                )

            except sqlite3.OperationalError:

                pass

        self.connection.commit()

    # ==========================================================
    # PRODUCT MIGRATIONS
    # ==========================================================

    def _run_product_migrations(self):

        columns = [
            ("target_price", "REAL DEFAULT 0"),
            ("target_alert_sent", "INTEGER DEFAULT 0"),
            ("last_recommendation", "TEXT DEFAULT ''"),
            ("recommendation_alert_sent", "INTEGER DEFAULT 0")
        ]

        for column_name, column_type in columns:

            try:

                self.cursor.execute(
                    f"""
                    ALTER TABLE products
                    ADD COLUMN {column_name} {column_type}
                    """
                )

            except sqlite3.OperationalError:

                pass

        self.connection.commit()

    # ==========================================================
    # USERS
    # ==========================================================

    def add_user(self, user):

        try:

            self.cursor.execute(
                """
                INSERT INTO users (

                    name,
                    email,
                    password_hash,
                    telegram_chat_id

                )

                VALUES (?, ?, ?, ?)
                """,
                (
                    user.name,
                    user.email,
                    user.password_hash,
                    user.telegram_chat_id
                )
            )

            self.connection.commit()

        except sqlite3.IntegrityError as error:

            raise Exception(
                "Email already registered."
            ) from error

    def get_user_by_email(self, email):

        self.cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        return self.cursor.fetchone()

    def get_user_by_id(self, user_id):

        self.cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )

        return self.cursor.fetchone()
    def get_user_by_google_id(
        self,
        google_id
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM users
            WHERE google_id = ?
            """,
            (google_id,)
        )

        return self.cursor.fetchone()

    def add_google_user(
        self,
        name,
        email,
        google_id
    ):

        try:

            self.cursor.execute(
                """
                INSERT INTO users (
                    name,
                    email,
                    password_hash,
                    telegram_chat_id,
                    auth_provider,
                    google_id
                )

                VALUES (?, ?, ?, '', 'google', ?)
                """,
                (
                    name,
                    email,
                    "",
                    google_id
                )
            )

            self.connection.commit()

            return self.cursor.lastrowid

        except sqlite3.IntegrityError as error:

            self.connection.rollback()

            raise Exception(
                "Unable to create Google account."
            ) from error

    def link_google_account(
        self,
        user_id,
        google_id
    ):

        self.cursor.execute(
            """
            UPDATE users
            SET google_id = ?
            WHERE id = ?
            """,
            (
                google_id,
                user_id
            )
        )

        self.connection.commit()

    def update_user_settings(
        self,
        user_id,
        name,
        telegram_chat_id,
        telegram_notifications,
        target_price_alerts,
        deal_score_alerts,
        price_drop_alerts
    ):

        self.cursor.execute(
            """
            UPDATE users

            SET
                name = ?,
                telegram_chat_id = ?,
                telegram_notifications = ?,
                target_price_alerts = ?,
                deal_score_alerts = ?,
                price_drop_alerts = ?

            WHERE id = ?
            """,
            (
                name,
                telegram_chat_id,
                int(telegram_notifications),
                int(target_price_alerts),
                int(deal_score_alerts),
                int(price_drop_alerts),
                user_id
            )
        )

        self.connection.commit()

        if self.cursor.rowcount == 0:

            raise Exception(
                "User not found."
            )

    # ==========================================================
    # PRODUCT CREATE
    # ==========================================================

    def add_product(self, product):

        try:

            self.cursor.execute(
                """
                INSERT INTO products (

                    user_id,
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

                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    product.user_id,
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

            product_id = self.cursor.lastrowid

            if (
                product.current_price is not None
                and product.current_price > 0
            ):

                self.cursor.execute(
                    """
                    INSERT INTO price_history (
                        product_id,
                        price
                    )

                    VALUES (?, ?)
                    """,
                    (
                        product_id,
                        product.current_price
                    )
                )

            self.connection.commit()

            return product_id

        except sqlite3.IntegrityError as error:

            self.connection.rollback()

            raise Exception(
                "This product is already being tracked."
            ) from error

    # ==========================================================
    # PRODUCT READ
    # ==========================================================

    def get_all_products(self, user_id):

        self.cursor.execute(
            """
            SELECT *
            FROM products

            WHERE
                user_id = ?
                AND active = 1

            ORDER BY id DESC
            """,
            (user_id,)
        )

        return self.cursor.fetchall()

    def get_all_active_products(self):

        self.cursor.execute(
            """
            SELECT *
            FROM products

            WHERE active = 1

            ORDER BY id ASC
            """
        )

        return self.cursor.fetchall()

    def get_product_by_id(
        self,
        product_id,
        user_id=None
    ):

        if user_id is None:

            self.cursor.execute(
                """
                SELECT *
                FROM products
                WHERE id = ?
                """,
                (product_id,)
            )

        else:

            self.cursor.execute(
                """
                SELECT *
                FROM products

                WHERE
                    id = ?
                    AND user_id = ?
                """,
                (
                    product_id,
                    user_id
                )
            )

        return self.cursor.fetchone()

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

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search_products(
        self,
        user_id,
        search
    ):

        search = search.strip()

        self.cursor.execute(
            """
            SELECT *
            FROM products

            WHERE
                user_id = ?
                AND active = 1
                AND LOWER(name) LIKE LOWER(?)

            ORDER BY name ASC

            LIMIT 10
            """,
            (
                user_id,
                f"%{search}%"
            )
        )

        return self.cursor.fetchall()

    # ==========================================================
    # PRODUCT UPDATE
    # ==========================================================

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

            WHERE
                product_url = ?
                AND user_id = ?
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
                product.product_url,
                product.user_id
            )
        )

        self.connection.commit()

    def update_metadata(self, product):

        self.cursor.execute(
            """
            UPDATE products

            SET
                name = ?,
                current_price = ?,
                previous_price = ?,
                lowest_price = ?,
                highest_price = ?,
                affiliate_url = ?,
                image = ?,
                rating = ?,
                reviews = ?,
                availability = ?,
                prime = ?,
                last_checked = CURRENT_TIMESTAMP

            WHERE
                asin = ?
                AND user_id = ?
            """,
            (
                product.name,
                product.current_price,
                product.previous_price,
                product.lowest_price,
                product.highest_price,
                product.affiliate_url,
                product.image,
                product.rating,
                product.reviews,
                product.availability,
                int(product.prime),
                product.asin,
                product.user_id
            )
        )

        self.connection.commit()

    # ==========================================================
    # TARGET PRICE
    # ==========================================================

    def update_target_price(
        self,
        product_id,
        user_id,
        target_price
    ):

        self.cursor.execute(
            """
            UPDATE products

            SET
                target_price = ?,
                target_alert_sent = 0

            WHERE
                id = ?
                AND user_id = ?
            """,
            (
                target_price,
                product_id,
                user_id
            )
        )

        self.connection.commit()

        if self.cursor.rowcount == 0:

            raise Exception(
                "Product not found or access denied."
            )

    def mark_target_alert_sent(
        self,
        product_id
    ):

        self.cursor.execute(
            """
            UPDATE products
            SET target_alert_sent = 1
            WHERE id = ?
            """,
            (product_id,)
        )

        self.connection.commit()

    def reset_target_alert(
        self,
        product_id
    ):

        self.cursor.execute(
            """
            UPDATE products
            SET target_alert_sent = 0
            WHERE id = ?
            """,
            (product_id,)
        )

        self.connection.commit()

    # ==========================================================
    # BUY RECOMMENDATION ALERT
    # ==========================================================

    def update_recommendation_status(
        self,
        product_id,
        recommendation
    ):

        self.cursor.execute(
            """
            UPDATE products

            SET
                recommendation_alert_sent =
                    CASE
                        WHEN last_recommendation != ?
                        THEN 0
                        ELSE recommendation_alert_sent
                    END,
                last_recommendation = ?

            WHERE id = ?
            """,
            (
                recommendation,
                recommendation,
                product_id
            )
        )

        self.connection.commit()

    def mark_recommendation_alert_sent(
        self,
        product_id
    ):

        self.cursor.execute(
            """
            UPDATE products
            SET recommendation_alert_sent = 1
            WHERE id = ?
            """,
            (product_id,)
        )

        self.connection.commit()

    # ==========================================================
    # PENDING OTP REGISTRATIONS
    # ==========================================================

    def save_pending_registration(
        self,
        name,
        email,
        password_hash,
        otp_hash,
        otp_expires_at
    ):

        self.cursor.execute(
            """
            INSERT INTO pending_registrations (
                name,
                email,
                password_hash,
                otp_hash,
                otp_expires_at,
                otp_attempts,
                last_otp_sent_at
            )

            VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)

            ON CONFLICT(email) DO UPDATE SET
                name = excluded.name,
                password_hash = excluded.password_hash,
                otp_hash = excluded.otp_hash,
                otp_expires_at = excluded.otp_expires_at,
                otp_attempts = 0,
                last_otp_sent_at = CURRENT_TIMESTAMP
            """,
            (
                name,
                email,
                password_hash,
                otp_hash,
                otp_expires_at
            )
        )

        self.connection.commit()

    def get_pending_registration(self, email):

        self.cursor.execute(
            """
            SELECT *
            FROM pending_registrations
            WHERE email = ?
            """,
            (email,)
        )

        return self.cursor.fetchone()

    def increment_otp_attempts(self, email):

        self.cursor.execute(
            """
            UPDATE pending_registrations
            SET otp_attempts = otp_attempts + 1
            WHERE email = ?
            """,
            (email,)
        )

        self.connection.commit()

    def delete_pending_registration(self, email):

        self.cursor.execute(
            """
            DELETE FROM pending_registrations
            WHERE email = ?
            """,
            (email,)
        )

        self.connection.commit()

    # ==========================================================
    # PRICE HISTORY
    # ==========================================================

    def add_price_history(
        self,
        product_id,
        price
    ):

        if (
            price is None
            or price <= 0
        ):

            return

        self.cursor.execute(
            """
            INSERT INTO price_history (
                product_id,
                price
            )

            VALUES (?, ?)
            """,
            (
                product_id,
                price
            )
        )

        self.connection.commit()

    def get_price_history(
        self,
        product_id,
        user_id
    ):

        self.cursor.execute(
            """
            SELECT
                price_history.price,
                price_history.checked_at

            FROM price_history

            INNER JOIN products
                ON products.id =
                   price_history.product_id

            WHERE
                price_history.product_id = ?
                AND products.user_id = ?

            ORDER BY
                price_history.checked_at ASC,
                price_history.id ASC
            """,
            (
                product_id,
                user_id
            )
        )

        return self.cursor.fetchall()

    # ==========================================================
    # ANALYTICS
    # ==========================================================

    def get_analytics_summary(self, user_id):

        self.cursor.execute(
            """
            SELECT

                COUNT(*) AS total_products,

                SUM(
                    CASE

                        WHEN previous_price > current_price
                        THEN 1

                        ELSE 0

                    END
                ) AS price_drops,

                COALESCE(
                    SUM(
                        CASE

                            WHEN previous_price > current_price

                            THEN
                                previous_price
                                - current_price

                            ELSE 0

                        END
                    ),
                    0
                ) AS total_savings,

                COALESCE(
                    MAX(
                        CASE

                            WHEN previous_price > current_price

                            THEN
                                previous_price
                                - current_price

                            ELSE 0

                        END
                    ),
                    0
                ) AS biggest_drop

            FROM products

            WHERE
                user_id = ?
                AND active = 1
            """,
            (user_id,)
        )

        return self.cursor.fetchone()

    def get_recent_price_activity(
        self,
        user_id,
        limit=10
    ):

        self.cursor.execute(
            """
            SELECT
                products.id AS product_id,
                products.name,
                products.image,
                price_history.price,
                price_history.checked_at

            FROM price_history

            INNER JOIN products
                ON products.id =
                   price_history.product_id

            WHERE
                products.user_id = ?
                AND products.active = 1

            ORDER BY
                price_history.checked_at DESC,
                price_history.id DESC

            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        )

        return self.cursor.fetchall()

    def get_analytics_chart(self, user_id):

        self.cursor.execute(
            """
            SELECT
                DATE(
                    price_history.checked_at
                ) AS scan_date,

                ROUND(
                    AVG(price_history.price),
                    2
                ) AS average_price

            FROM price_history

            INNER JOIN products
                ON products.id =
                   price_history.product_id

            WHERE
                products.user_id = ?
                AND products.active = 1

            GROUP BY
                DATE(price_history.checked_at)

            ORDER BY
                scan_date ASC
            """,
            (user_id,)
        )

        return self.cursor.fetchall()

    # ==========================================================
    # SCAN RUN TRACKING
    # ==========================================================

    def create_scan_run(
        self,
        started_at,
        total_products
    ):

        self.cursor.execute(
            """
            INSERT INTO scan_runs (

                started_at,
                status,
                total_products,
                checked_products,
                failed_products

            )

            VALUES (?, 'RUNNING', ?, 0, 0)
            """,
            (
                started_at,
                total_products
            )
        )

        scan_run_id = self.cursor.lastrowid

        self.connection.commit()

        return scan_run_id

    def complete_scan_run(
        self,
        scan_run_id,
        completed_at,
        status,
        checked_products,
        failed_products,
        duration_seconds,
        error_message=""
    ):

        self.cursor.execute(
            """
            UPDATE scan_runs

            SET
                completed_at = ?,
                status = ?,
                checked_products = ?,
                failed_products = ?,
                duration_seconds = ?,
                error_message = ?

            WHERE id = ?
            """,
            (
                completed_at,
                status,
                checked_products,
                failed_products,
                duration_seconds,
                error_message,
                scan_run_id
            )
        )

        self.connection.commit()

    def get_latest_scan_run(self):

        self.cursor.execute(
            """
            SELECT *
            FROM scan_runs

            ORDER BY id DESC

            LIMIT 1
            """
        )

        return self.cursor.fetchone()

    def get_recent_scan_runs(
        self,
        limit=10
    ):

        self.cursor.execute(
            """
            SELECT *
            FROM scan_runs

            ORDER BY id DESC

            LIMIT ?
            """,
            (limit,)
        )

        return self.cursor.fetchall()

    # ==========================================================
    # DELETE PRODUCT
    # ==========================================================

    def delete_product(
        self,
        product_id,
        user_id=None
    ):

        if user_id is None:

            self.cursor.execute(
                """
                DELETE FROM products
                WHERE id = ?
                """,
                (product_id,)
            )

        else:

            self.cursor.execute(
                """
                DELETE FROM products

                WHERE
                    id = ?
                    AND user_id = ?
                """,
                (
                    product_id,
                    user_id
                )
            )

        self.connection.commit()

    # ==========================================================
    # CLOSE
    # ==========================================================

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None

            logger.info(
                "Database Connection Closed"
            )
