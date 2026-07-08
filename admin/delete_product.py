from engine.product_service import ProductService


def delete_product():

    product_id = int(input("\nEnter Product ID : "))

    service = ProductService()

    service.delete_product(product_id)

    service.close()

    print("\n✅ Product Deleted")
