from flask import render_template

from engine.product_service import ProductService


def register_routes(app):

    @app.route("/")
    def home():

        service = ProductService()

        products = service.get_all_products()

        service.close()

        return render_template(
            "index.html",
            total_products=len(products),
            products=products
        )
