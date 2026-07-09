from werkzeug.security import generate_password_hash, check_password_hash

from database.database import Database
from models.user import User


class UserService:

    def __init__(self):
        self.db = Database()

    def register(self, name, email, password):

        existing = self.db.get_user_by_email(email)

        if existing:
            raise Exception("Email already registered.")

        password_hash = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )

        self.db.add_user(user)

    def login(self, email, password):

        user = self.db.get_user_by_email(email)

        if user is None:
            return None

        if check_password_hash(user["password_hash"], password):
            return user

        return None

    def close(self):
        self.db.close()
