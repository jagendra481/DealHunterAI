from flask import render_template, request, redirect, url_for, flash

from engine.product_service import ProductService
from providers.amazon_provider import AmazonProvider
from services.affiliate_service import AffiliateService


def register_routes(app):

    @app.route("/")
    def dashboard():

        service = ProductService()

        products = service.get_all_products()

        total_products = len(products)

        ratings = [p["rating"] for p in products if p["rating"] > 0]

        avg_rating = (
            round(sum(ratings) / len(ratings), 1)
            if ratings else 0
        )

        avg_price = (
            round(
                sum(p["current_price"] for p in products) / total_products,
                2
            )
            if total_products else 0
        )

        service.close()

        return render_template(
            "index.html",
            total_products=total_products,
            avg_rating=avg_rating,
            avg_price=avg_price
        )

    @app.route("/products")
    def products():

        service = ProductService()

        products = service.get_all_products()

        service.close()

        return render_template(
            "products.html",
            products=products
        )

    @app.route("/add-product", methods=["GET", "POST"])
    def add_product():

        if request.method == "POST":

            try:

                url = request.form["url"]

                product = AmazonProvider.get_product(url)

                product.affiliate_url = AffiliateService.generate_amazon_link(url)

                service = ProductService()

                service.add_product(product)

                service.close()

                flash("✅ Product added successfully!", "success")

                return redirect(url_for("products"))

            except Exception as e:

                flash(str(e), "danger")

        return render_template("add_product.html")

    @app.route("/delete-product/<int:product_id>")
    def delete_product(product_id):

        try:

            service = ProductService()

            service.delete_product(product_id)

            service.close()

            flash("✅ Product deleted successfully!", "success")

        except Exception as e:

            flash(str(e), "danger")

        return redirect(url_for("products"))

    @app.route("/refresh-product/<int:product_id>")
    def refresh_product(product_id):

        try:

            service = ProductService()

            service.refresh_product(product_id)

            service.close()

            flash("✅ Product refreshed successfully!", "success")

        except Exception as e:

            flash(str(e), "danger")

        return redirect(url_for("products"))
