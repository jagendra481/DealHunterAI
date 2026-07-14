from engine.recommendation_engine import RecommendationEngine
from engine.product_service import ProductService
from sources.source_manager import SourceManager
from engine.price_comparator import PriceComparator
from engine.deal_scorer import DealScorer

from services.telegram_service import TelegramService
from services.user_service import UserService

import traceback


class DealEngine:

    def __init__(self):

        self.product_service = ProductService()
        self.user_service = UserService()

    # ==========================================================
    # RUN ENGINE
    # ==========================================================

    def run(self):

        print("\n========== DEAL ENGINE ==========\n")

        try:

            products = (
                self.product_service
                .get_all_active_products()
            )

            print("=" * 60)
            print("TOTAL PRODUCTS:", len(products))

            for product in products:

                print(f"• {product['name']}")

            print("=" * 60)

            if not products:

                print("No Products Found")

                return

            for product in products:

                self._check_product(product)

        finally:

            self.product_service.close()
            self.user_service.close()

    # ==========================================================
    # CHECK PRODUCT
    # ==========================================================

    def _check_product(self, product):

        try:

            print(
                f"\nChecking: {product['name']}"
            )

            user = self.user_service.get_user_by_id(
                product["user_id"]
            )

            if user is None:

                print(
                    "⚠️ Product owner not found."
                )

                return

            source = SourceManager.get_source(
                product["product_url"]
            )

            latest_product = source.fetch_product(
                product
            )

            latest_product.user_id = (
                product["user_id"]
            )

            latest_product.product_url = (
                product["product_url"]
            )

            latest_product.affiliate_url = (
                product["affiliate_url"]
            )

            old_price = float(
                product["current_price"] or 0
            )

            new_price = float(
                latest_product.current_price or 0
            )

            # ==================================================
            # VALIDATE PRICE
            # ==================================================

            if new_price <= 0:

                print(
                    "⚠️ Invalid product price. "
                    "Skipping product."
                )

                return

            # ==================================================
            # SAVE PRICE HISTORY
            # ==================================================

            self.product_service.add_price_history(
                product["id"],
                new_price
            )

            print(
                f"📊 Price History Saved: "
                f"₹{new_price:,.0f}"
            )

            # ==================================================
            # COMPARE PRICE
            # ==================================================
            history = self.product_service.get_price_history(
                product["id"],
                product["user_id"]
            )

            recommendation = RecommendationEngine.analyze(
                latest_product.current_price,
                [
                    row["price"]
                    for row in history
                ]
            )

            print(
                "AI Recommendation:",
                recommendation["recommendation"]
            )
            last_recommendation = (
                product.get("last_recommendation")
                or "COLLECTING"
            )

            alert_sent = bool(
                product.get(
                    "recommendation_alert_sent",
                    0
                )
            )

            if (
                recommendation["recommendation"] == "BUY_NOW"
                and last_recommendation != "BUY_NOW"
                and not alert_sent
            ):

                if (
                    user.telegram_notifications
                    and user.telegram_chat_id
                ):

                    TelegramService.send_buy_now_alert(
                        latest_product,
                        recommendation,
                        user.telegram_chat_id
                    )

                    self.product_service.mark_recommendation_alert_sent(
                        product["id"]
                    )

                    print(
                        "🟢 BUY NOW alert sent."
                    )

            self.product_service.update_recommendation_status(
                product["id"],
                recommendation["recommendation"]
            )

            status = PriceComparator.compare(
                old_price,
                new_price
            )

            score = DealScorer.calculate(
                old_price,
                new_price
            )

            print("--------------------------------------")
            print("Product    :", latest_product.name)
            print("Old Price  :", old_price)
            print("New Price  :", new_price)
            print("Status     :", status)
            print("Deal Score :", score)
            print("--------------------------------------")

            # ==================================================
            # TARGET PRICE ALERT
            # ==================================================

            self._check_target_price(
                product,
                latest_product,
                user
            )

            # ==================================================
            # PRICE DROP
            # ==================================================

            if status == "DROP":

                self._handle_price_drop(
                    product,
                    latest_product,
                    old_price,
                    score,
                    user
                )

            elif status == "SAME":

                print("ℹ️ Price unchanged.")

            else:

                print("📈 Price increased.")

                self._update_product_price(
                    product,
                    latest_product,
                    old_price
                )

        except Exception:

            print(
                f"\n❌ Error checking "
                f"{product['name']}"
            )

            traceback.print_exc()

    # ==========================================================
    # TARGET PRICE CHECK
    # ==========================================================

    def _check_target_price(
        self,
        product,
        latest_product,
        user
    ):

        target_price = float(
            product["target_price"] or 0
        )

        current_price = float(
            latest_product.current_price or 0
        )

        alert_sent = bool(
            product["target_alert_sent"]
        )

        if target_price <= 0:

            return

        if current_price > target_price:

            if alert_sent:

                self.product_service.reset_target_alert(
                    product["id"]
                )

                print(
                    "🔄 Target alert re-armed."
                )

            return

        print(
            f"🎯 Target reached: "
            f"₹{current_price:,.0f} <= "
            f"₹{target_price:,.0f}"
        )

        if alert_sent:

            print(
                "ℹ️ Target alert already sent."
            )

            return

        if not user.telegram_notifications:

            print(
                "🔕 Telegram notifications disabled."
            )

            return

        if not user.target_price_alerts:

            print(
                "🔕 Target price alerts disabled."
            )

            return

        if not user.telegram_chat_id:

            print(
                "⚠️ Telegram Chat ID not configured."
            )

            return

        TelegramService.send_target_price_alert(
            latest_product,
            target_price,
            user.telegram_chat_id
        )

        self.product_service.mark_target_alert_sent(
            product["id"]
        )

        print(
            f"✅ Target price alert sent "
            f"to User {user.id}"
        )

    # ==========================================================
    # HANDLE PRICE DROP
    # ==========================================================

    def _handle_price_drop(
        self,
        product,
        latest_product,
        old_price,
        score,
        user
    ):

        self._update_product_price(
            product,
            latest_product,
            old_price
        )

        print("✅ Database Updated")

        if not user.telegram_notifications:

            print(
                "🔕 Telegram notifications disabled."
            )

            return

        if not user.telegram_chat_id:

            print(
                "⚠️ Telegram Chat ID not configured."
            )

            return

        # ======================================================
        # DEAL SCORE ALERT
        # ======================================================

        if (
            score >= 60
            and user.deal_score_alerts
        ):

            TelegramService.send_photo(
                latest_product,
                old_price,
                score,
                user.telegram_chat_id
            )

            print(
                f"🔥 Deal score alert sent "
                f"to User {user.id}"
            )

            return

        # ======================================================
        # PRICE DROP ALERT
        # ======================================================

        if user.price_drop_alerts:

            TelegramService.send_price_drop_alert(
                latest_product,
                old_price,
                user.telegram_chat_id
            )

            print(
                f"📉 Price drop alert sent "
                f"to User {user.id}"
            )

            return

        print(
            "🔕 Price drop notification skipped."
        )

    # ==========================================================
    # UPDATE PRODUCT PRICE
    # ==========================================================

    def _update_product_price(
        self,
        product,
        latest_product,
        old_price
    ):

        latest_product.previous_price = old_price

        existing_lowest = (
            product["lowest_price"]
            or old_price
            or latest_product.current_price
        )

        existing_highest = (
            product["highest_price"]
            or old_price
            or latest_product.current_price
        )

        latest_product.lowest_price = min(
            existing_lowest,
            latest_product.current_price
        )

        latest_product.highest_price = max(
            existing_highest,
            latest_product.current_price
        )

        latest_product.last_checked = "NOW"

        self.product_service.update_product(
            latest_product
        )
