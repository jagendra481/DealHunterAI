from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import login_required, current_user

from engine.product_service import ProductService
from engine.recommendation_engine import RecommendationEngine

from providers.amazon_provider import AmazonProvider

from services.affiliate_service import AffiliateService
from services.user_service import UserService
from services.telegram_service import TelegramService


# ==========================================================
# PRICE INTELLIGENCE BUILDER
# ==========================================================

def build_price_intelligence(
    service,
    products,
    user_id
):

    intelligence_products = []

    for product in products:

        history = service.get_price_history(
            product["id"],
            user_id
        )

        valid_history = [
            row
            for row in history
            if (
                row["price"] is not None
                and row["price"] > 0
            )
        ]

        prices = [
            float(row["price"])
            for row in valid_history
        ]

        labels = [
            row["checked_at"]
            for row in valid_history
        ]

        recommendation = RecommendationEngine.analyze(
            product["current_price"],
            prices
        )

        intelligence_products.append(
            {
                "id": product["id"],
                "name": product["name"],
                "image": product["image"],
                "current_price": float(
                    product["current_price"] or 0
                ),
                "lowest_price": recommendation.get(
                    "lowest_price",
                    float(
                        product["current_price"] or 0
                    )
                ),
                "highest_price": recommendation.get(
                    "highest_price",
                    float(
                        product["current_price"] or 0
                    )
                ),
                "above_low_percent": recommendation.get(
                    "above_low_percent",
                    0
                ),
                "trend": recommendation.get(
                    "trend",
                    "STABLE"
                ),
                "insight": recommendation[
                    "recommendation"
                ],
                "recommendation": recommendation[
                    "recommendation"
                ],
                "confidence": recommendation[
                    "confidence"
                ],
                "reason": recommendation[
                    "reason"
                ],
                "estimated_saving": recommendation[
                    "estimated_saving"
                ],
                "scan_count": recommendation.get(
                    "scan_count",
                    len(prices)
                ),
                "labels": labels,
                "prices": prices
            }
        )

    recommendation_priority = {
        "BUY_NOW": 0,
        "WAIT": 1,
        "EXPENSIVE": 2,
        "COLLECTING": 3
    }

    intelligence_products.sort(
        key=lambda item: (
            recommendation_priority.get(
                item["recommendation"],
                4
            ),
            -item["confidence"]
        )
    )

    return intelligence_products


# ==========================================================
# REGISTER ROUTES
# ==========================================================

def register_routes(app):
        # ==========================================================
    # ABOUT DEALHUNTERAI
    # ==========================================================

    @app.route("/about")
    @login_required
    def about():

        return render_template(
            "about/index.html"
        )

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    @app.route("/")
    @login_required
    def dashboard():

        service = ProductService()

        try:

            products = service.get_all_products(
                current_user.id
            )

            total_products = len(products)

            ratings = [
                product["rating"]
                for product in products
                if product["rating"] > 0
            ]

            avg_rating = (
                round(
                    sum(ratings) / len(ratings),
                    1
                )
                if ratings
                else 0
            )

            intelligence_products = (
                build_price_intelligence(
                    service,
                    products,
                    current_user.id
                )
            )

            good_opportunities = sum(
                1
                for product in intelligence_products
                if (
                    product["recommendation"]
                    == "BUY_NOW"
                )
            )

            falling_prices = sum(
                1
                for product in intelligence_products
                if (
                    product["trend"] == "FALLING"
                    and product["recommendation"]
                    != "COLLECTING"
                )
            )

            best_opportunities = (
                intelligence_products[:5]
            )

        finally:

            service.close()

        return render_template(
            "dashboard/index.html",
            total_products=total_products,
            avg_rating=avg_rating,
            good_opportunities=good_opportunities,
            falling_prices=falling_prices,
            best_opportunities=best_opportunities
        )

    # ==========================================================
    # PRODUCTS
    # ==========================================================

    @app.route("/products")
    @login_required
    def products():

        search = request.args.get(
            "search",
            ""
        ).strip()

        service = ProductService()

        try:

            if search:

                product_list = service.search_products(
                    current_user.id,
                    search
                )

            else:

                product_list = service.get_all_products(
                    current_user.id
                )

        finally:

            service.close()

        return render_template(
            "products/list.html",
            products=product_list,
            search=search
        )

    # ==========================================================
    # SEARCH API
    # ==========================================================

    @app.route("/api/search")
    @login_required
    def api_search():

        query = request.args.get(
            "q",
            ""
        ).strip()

        service = ProductService()

        try:

            product_list = service.search_products(
                current_user.id,
                query
            )

        finally:

            service.close()

        results = [
            {
                "id": product["id"],
                "name": product["name"]
            }
            for product in product_list
        ]

        return jsonify(results)

    # ==========================================================
    # ADD PRODUCT
    # ==========================================================

    @app.route(
        "/add-product",
        methods=["GET", "POST"]
    )
    @login_required
    def add_product():

        if request.method == "POST":

            service = None

            try:

                product_url = request.form.get(
                    "url",
                    ""
                ).strip()

                if not product_url:

                    raise Exception(
                        "Product URL is required."
                    )

                product = AmazonProvider.get_product(
                    product_url
                )

                product.user_id = current_user.id

                product.affiliate_url = (
                    AffiliateService
                    .generate_amazon_link(
                        product_url
                    )
                )

                service = ProductService()

                service.add_product(product)

                flash(
                    "Product added successfully!",
                    "success"
                )

                return redirect(
                    url_for("products")
                )

            except Exception as error:

                flash(
                    str(error),
                    "danger"
                )

            finally:

                if service is not None:

                    service.close()

        return render_template(
            "products/add.html"
        )

    # ==========================================================
    # PRODUCT DETAILS
    # ==========================================================

    @app.route("/product/<int:product_id>")
    @login_required
    def product_details(product_id):

        service = ProductService()

        try:

            product = service.get_product_by_id(
                product_id,
                current_user.id
            )

            if product is None:

                flash(
                    "Product not found or access denied.",
                    "danger"
                )

                return redirect(
                    url_for("products")
                )

            price_history = service.get_price_history(
                product_id,
                current_user.id
            )

            valid_history = [
                row
                for row in price_history
                if (
                    row["price"] is not None
                    and row["price"] > 0
                )
            ]

            history_labels = [
                row["checked_at"]
                for row in valid_history
            ]

            history_prices = [
                float(row["price"])
                for row in valid_history
            ]

            recommendation = (
                RecommendationEngine.analyze(
                    product["current_price"],
                    history_prices
                )
            )

            return render_template(
                "products/details.html",
                product=product,
                history_labels=history_labels,
                history_prices=history_prices,
                recommendation=recommendation
            )

        finally:

            service.close()

    # ==========================================================
    # TARGET PRICE
    # ==========================================================

    @app.route(
        "/product/<int:product_id>/target-price",
        methods=["POST"]
    )
    @login_required
    def update_target_price(product_id):

        service = ProductService()

        redirect_page = request.form.get(
            "redirect_page",
            "product"
        )

        try:

            target_value = request.form.get(
                "target_price",
                ""
            ).strip()

            if not target_value:

                target_price = 0

            else:

                target_price = float(
                    target_value
                )

            if target_price < 0:

                raise ValueError

            service.update_target_price(
                product_id,
                current_user.id,
                target_price
            )

            if target_price > 0:

                flash(
                    "Target price saved successfully!",
                    "success"
                )

            else:

                flash(
                    "Target price alert removed.",
                    "success"
                )

        except ValueError:

            flash(
                "Please enter a valid target price.",
                "danger"
            )

        except Exception as error:

            flash(
                str(error),
                "danger"
            )

        finally:

            service.close()

        if redirect_page == "alerts":

            return redirect(
                url_for("alerts")
            )

        return redirect(
            url_for(
                "product_details",
                product_id=product_id
            )
        )

    # ==========================================================
    # ALERTS
    # ==========================================================

    @app.route("/alerts")
    @login_required
    def alerts():

        service = ProductService()

        try:

            product_list = service.get_all_products(
                current_user.id
            )

            active_alerts = sum(
                1
                for product in product_list
                if (
                    product["target_price"]
                    and product["target_price"] > 0
                )
            )

            watching_alerts = sum(
                1
                for product in product_list
                if (
                    product["target_price"]
                    and product["target_price"] > 0
                    and float(
                        product["current_price"] or 0
                    )
                    > float(product["target_price"])
                )
            )

            reached_alerts = sum(
                1
                for product in product_list
                if (
                    product["target_price"]
                    and product["target_price"] > 0
                    and float(
                        product["current_price"] or 0
                    )
                    <= float(product["target_price"])
                )
            )

        finally:

            service.close()

        return render_template(
            "alerts/index.html",
            products=product_list,
            active_alerts=active_alerts,
            watching_alerts=watching_alerts,
            reached_alerts=reached_alerts
        )

    # ==========================================================
    # DELETE PRODUCT
    # ==========================================================

    @app.route(
        "/delete-product/<int:product_id>",
        methods=["POST"]
    )
    @login_required
    def delete_product(product_id):

        service = ProductService()

        try:

            service.delete_product(
                product_id,
                current_user.id
            )

            flash(
                "Product deleted successfully!",
                "success"
            )

        except Exception as error:

            flash(
                str(error),
                "danger"
            )

        finally:

            service.close()

        return redirect(
            url_for("products")
        )

    # ==========================================================
    # REFRESH PRODUCT
    # ==========================================================

    @app.route(
        "/refresh-product/<int:product_id>",
        methods=["POST"]
    )
    @login_required
    def refresh_product(product_id):

        service = ProductService()

        try:

            service.refresh_product(
                product_id,
                current_user.id
            )

            flash(
                "Product refreshed successfully!",
                "success"
            )

        except Exception as error:

            flash(
                str(error),
                "danger"
            )

        finally:

            service.close()

        return redirect(
            url_for("products")
        )

    # ==========================================================
    # ANALYTICS
    # ==========================================================

    @app.route("/analytics")
    @login_required
    def analytics():

        service = ProductService()

        try:

            products = service.get_all_products(
                current_user.id
            )

            analytics_products = (
                build_price_intelligence(
                    service,
                    products,
                    current_user.id
                )
            )

        finally:

            service.close()

        return render_template(
            "analytics/index.html",
            analytics_products=analytics_products
        )

    # ==========================================================
    # PROFILE
    # ==========================================================

    @app.route("/profile")
    @login_required
    def profile():

        service = ProductService()

        try:

            product_list = service.get_all_products(
                current_user.id
            )

            total_products = len(product_list)

            ratings = [
                product["rating"]
                for product in product_list
                if product["rating"] > 0
            ]

            avg_rating = (
                round(
                    sum(ratings) / len(ratings),
                    1
                )
                if ratings
                else 0
            )

            total_value = sum(
                product["current_price"] or 0
                for product in product_list
            )

        finally:

            service.close()

        return render_template(
            "profile/index.html",
            user=current_user,
            total_products=total_products,
            avg_rating=avg_rating,
            total_value=total_value
        )

    # ==========================================================
    # TELEGRAM TEST
    # ==========================================================

    @app.route(
        "/settings/test-telegram",
        methods=["POST"]
    )
    @login_required
    def test_telegram():

        service = UserService()

        try:

            user = service.get_user_by_id(
                current_user.id
            )

            if user is None:

                raise Exception(
                    "User not found."
                )

            if not user.telegram_chat_id:

                raise Exception(
                    "Please save your Telegram Chat ID first."
                )

            message = """
🔔 <b>DealHunterAI Test Alert</b>

Your Telegram connection is working successfully! 🚀

Notification preferences are configured in your account.

🤖 <b>DealHunterAI</b>
"""

            TelegramService.send_message(
                message,
                user.telegram_chat_id
            )

            flash(
                "Test Telegram alert sent successfully!",
                "success"
            )

        except Exception as error:

            flash(
                str(error),
                "danger"
            )

        finally:

            service.close()

        return redirect(
            url_for("settings")
        )

    # ==========================================================
    # SETTINGS
    # ==========================================================

    @app.route(
        "/settings",
        methods=["GET", "POST"]
    )
    @login_required
    def settings():

        service = UserService()

        try:

            if request.method == "POST":

                name = request.form.get(
                    "name",
                    ""
                ).strip()

                telegram_chat_id = request.form.get(
                    "telegram_chat_id",
                    ""
                ).strip()

                telegram_notifications = (
                    "telegram_notifications"
                    in request.form
                )

                target_price_alerts = (
                    "target_price_alerts"
                    in request.form
                )

                deal_score_alerts = (
                    "deal_score_alerts"
                    in request.form
                )

                price_drop_alerts = (
                    "price_drop_alerts"
                    in request.form
                )

                service.update_settings(
                    current_user.id,
                    name,
                    telegram_chat_id,
                    telegram_notifications,
                    target_price_alerts,
                    deal_score_alerts,
                    price_drop_alerts
                )

                flash(
                    "Settings updated successfully!",
                    "success"
                )

                return redirect(
                    url_for("settings")
                )

            user = service.get_user_by_id(
                current_user.id
            )

            if user is None:

                raise Exception(
                    "User not found."
                )

            return render_template(
                "settings/index.html",
                user=user
            )

        except Exception as error:

            flash(
                str(error),
                "danger"
            )

            return redirect(
                url_for("dashboard")
            )

        finally:

            service.close()

