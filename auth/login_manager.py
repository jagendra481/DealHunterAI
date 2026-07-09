from flask_login import LoginManager

from database.database import Database
from models.user import User

login_manager = LoginManager()

login_manager.login_view = "login"
login_manager.login_message = "Please login to continue."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):

    db = Database()

    row = db.get_user_by_id(user_id)

    db.close()

    if row is None:
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
