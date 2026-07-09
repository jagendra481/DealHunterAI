from dataclasses import dataclass
from flask_login import UserMixin


@dataclass
class User(UserMixin):

    id: int = None

    name: str = ""

    email: str = ""

    password_hash: str = ""

    telegram_chat_id: str = ""

    is_admin: bool = False

    is_active: bool = True
