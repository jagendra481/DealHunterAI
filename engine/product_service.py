from database.database import Database


class ProductService:

    def __init__(self):

        self.db = Database()

    def add_product(self, product):

        self.db.add_product(product)

    def get_all_products(self):

        return self.db.get_all_products()

    def close(self):

        self.db.close()
