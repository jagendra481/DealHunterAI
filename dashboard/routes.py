from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from engine.product_service import ProductService
from providers.amazon_provider import AmazonProvider
from services.affiliate_service import AffiliateService


def register_routes(app):

    # ==========================================================
    # Dashboard
    # ==========================================================

    @app.route("/")
    @login_required
    def dashboard():

        service = ProductService()

        products = service.get_all_products(current_user.id)

        total_products = len(products)

        ratings = [
            p["rating"]
            for p in products
            if p["rating"] > 0
        ]

        avg_rating = (
            round(sum(ratings) / len(ratings), 1)
            if ratings else 0
        )

        avg_price = (
            round(
                sum(p["current_price"] for p in products)
                / total_products,
                2
            )
            if total_products else 0
        )

        service.close()

        return render_template(
            "dashboard/index.html",
            total_products=total_products,
            avg_rating=avg_rating,
            avg_price=avg_price
        )

    # ==========================================================
    # Products
    # ==========================================================

    @app.route("/products")
    @login_required
    def products():

        search = request.args.get("search", "").strip()

        service = ProductService()

        if search:

            products = service.search_products(
                current_user.id,
                search
            )

        else:

            products = service.get_all_products(
                current_user.id
            )

        service.close()

        return render_template(
            "products/list.html",
            products=products,
            search=search
        )

    # ==========================================================
    # Add Product
    # ==========================================================

    @app.route("/add-product", methods=["GET", "POST"])
    @login_required
    def add_product():

        if request.method == "POST":

            try:

                url = request.form["url"].strip()

                product = AmazonProvider.get_product(url)

                # Assign current user
                product.user_id = current_user.id

                # Affiliate link
                product.affiliate_url = (
                    AffiliateService.generate_amazon_link(url)
                )

                service = ProductService()

                service.add_product(product)

                service.close()

                flash(
                    "✅ Product added successfully!",
                    "success"
                )

                return redirect(
                    url_for("products")
                )

            except Exception as e:

                flash(str(e), "danger")

        return render_template(
            "products/add.html"
        )

    # ==========================================================
    # Delete Product
    # ==========================================================

    @app.route("/delete-product/<int:product_id>")
    @login_required
    def delete_product(product_id):

        try:

            service = ProductService()

            service.delete_product(product_id)

            service.close()

            flash(
                "✅ Product deleted successfully!",
                "success"
            )

        except Exception as e:

            flash(str(e), "danger")

        return redirect(
            url_for("products")
        )

    # ==========================================================
    # Refresh Product
    # ==========================================================

    @app.route("/refresh-product/<int:product_id>")
    @login_required
    def refresh_product(product_id):

        try:

            service = ProductService()

            service.refresh_product(product_id)

            service.close()

            flash(
                "✅ Product refreshed successfully!",
                "success"
            )

        except Exception as e:

            flash(str(e), "danger")

        return redirect(
            url_for("products")
        )

    # ==========================================================
    # Analytics
    # ==========================================================

    @app.route("/analytics")
    @login_required
    def analytics():

        return render_template(
            "analytics/index.html"
        )

    # ==========================================================
    # Settings
    # ==========================================================

    @app.route("/settings")
    @login_required
    def settings():

        return render_template(
            "settings/index.html"
        )
