from admin.add_product import add_product
from admin.list_products import list_products
from admin.delete_product import delete_product


def menu():

    while True:

        print("\n" + "=" * 45)
        print("        DealHunterAI Admin")
        print("=" * 45)

        print("1. Add Product")
        print("2. View Products")
        print("3. Delete Product")
        print("4. Exit")

        choice = input("\nEnter Choice : ")

        if choice == "1":
            add_product()

        elif choice == "2":
            list_products()

        elif choice == "3":
            delete_product()

        elif choice == "4":
            print("\nGood Bye 👋")
            break

        else:
            print("\nInvalid Choice")
