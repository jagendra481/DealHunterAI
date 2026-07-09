from dataclasses import dataclass


@dataclass
class User:

    id: int | None = None

    name: str = ""

    email: str = ""

    password_hash: str = ""

    telegram_chat_id: str = ""

    created_at: str = ""
