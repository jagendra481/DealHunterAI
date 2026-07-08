from database.database import Database


class ProductService:

    def __init__(self):
        self.db = Database()

    def add_product(self, product):
        self.db.add_product(product)

    def get_all_products(self):
        return self.db.get_all_products()

    def update_product(self, product):
        self.db.update_product(product)

    def close(self):
        self.db.close()
    def delete_product(self, product_id):
        self.db.delete_product(product_id)
