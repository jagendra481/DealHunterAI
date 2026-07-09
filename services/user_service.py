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

        row = self.db.get_user_by_email(email)

        if row is None:
            return None

        if not check_password_hash(row["password_hash"], password):
            return None

        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            telegram_chat_id=row["telegram_chat_id"],
            is_admin=bool(row["is_admin"]),
            is_active=bool(row["is_active"])
        )

    def close(self):
        self.db.close()
