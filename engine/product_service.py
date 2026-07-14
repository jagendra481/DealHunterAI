from database.database import Database
from providers.amazon_provider import AmazonProvider


class ProductService:

    def __init__(self):
        self.db = Database()

    # ==========================================================
    # PRODUCT CREATE
    # ==========================================================

    def add_product(self, product):
        return self.db.add_product(product)

    # ==========================================================
    # PRODUCT READ
    # ==========================================================

    def get_all_products(self, user_id):
        return self.db.get_all_products(user_id)

    def get_all_active_products(self):
        return self.db.get_all_active_products()

    def get_product_by_id(
        self,
        product_id,
        user_id=None
    ):

        return self.db.get_product_by_id(
            product_id,
            user_id
        )

    def get_product_by_asin(self, asin):
        return self.db.get_product_by_asin(asin)

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search_products(
        self,
        user_id,
        search
    ):

        return self.db.search_products(
            user_id,
            search
        )

    # ==========================================================
    # PRICE HISTORY
    # ==========================================================

    def add_price_history(
        self,
        product_id,
        price
    ):

        self.db.add_price_history(
            product_id,
            price
        )

    def get_price_history(
        self,
        product_id,
        user_id
    ):

        return self.db.get_price_history(
            product_id,
            user_id
        )

    # ==========================================================
    # TARGET PRICE
    # ==========================================================

    def update_target_price(
        self,
        product_id,
        user_id,
        target_price
    ):

        product = self.db.get_product_by_id(
            product_id,
            user_id
        )

        if product is None:

            raise Exception(
                "Product not found or access denied."
            )

        if target_price < 0:

            raise Exception(
                "Target price cannot be negative."
            )

        self.db.update_target_price(
            product_id,
            user_id,
            target_price
        )

    def mark_target_alert_sent(
        self,
        product_id
    ):

        self.db.mark_target_alert_sent(
            product_id
        )

    def reset_target_alert(
        self,
        product_id
    ):

        self.db.reset_target_alert(
            product_id
        )

    # ==========================================================
    # BUY RECOMMENDATION ALERT
    # ==========================================================

    def update_recommendation_status(
        self,
        product_id,
        recommendation
    ):

        self.db.update_recommendation_status(
            product_id,
            recommendation
        )

    def mark_recommendation_alert_sent(
        self,
        product_id
    ):

        self.db.mark_recommendation_alert_sent(
            product_id
        )

    # ==========================================================
    # ANALYTICS
    # ==========================================================

    def get_analytics_summary(self, user_id):

        return self.db.get_analytics_summary(
            user_id
        )

    def get_recent_price_activity(
        self,
        user_id,
        limit=10
    ):

        return self.db.get_recent_price_activity(
            user_id,
            limit
        )

    def get_analytics_chart(self, user_id):

        return self.db.get_analytics_chart(
            user_id
        )

    # ==========================================================
    # PRODUCT UPDATE
    # ==========================================================

    def update_product(self, product):
        self.db.update_product(product)

    def update_metadata(self, product):
        self.db.update_metadata(product)

    def refresh_product(
        self,
        product_id,
        user_id
    ):

        existing = self.db.get_product_by_id(
            product_id,
            user_id
        )

        if existing is None:

            raise Exception(
                "Product not found or access denied."
            )

        latest = AmazonProvider.get_product(
            existing["product_url"]
        )

        latest.user_id = existing["user_id"]

        latest.product_url = existing["product_url"]

        latest.affiliate_url = existing["affiliate_url"]

        latest.previous_price = (
            existing["current_price"]
        )

        existing_lowest = (
            existing["lowest_price"]
            or latest.current_price
        )

        existing_highest = (
            existing["highest_price"]
            or latest.current_price
        )

        latest.lowest_price = min(
            existing_lowest,
            latest.current_price
        )

        latest.highest_price = max(
            existing_highest,
            latest.current_price
        )

        self.db.update_metadata(latest)

        self.db.add_price_history(
            product_id,
            latest.current_price
        )

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete_product(
        self,
        product_id,
        user_id
    ):

        product = self.db.get_product_by_id(
            product_id,
            user_id
        )

        if product is None:

            raise Exception(
                "Product not found or access denied."
            )

        self.db.delete_product(
            product_id,
            user_id
        )

    # ==========================================================
    # CLOSE
    # ==========================================================

    def close(self):
        self.db.close()
