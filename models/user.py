from flask_login import UserMixin


class User(UserMixin):

    def __init__(
        self,
        id=None,
        name="",
        email="",
        password_hash="",
        telegram_chat_id="",
        auth_provider="password",
        google_id="",
        is_admin=0,
        is_active=1
    ):

        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.telegram_chat_id = telegram_chat_id

        self.auth_provider = auth_provider
        self.google_id = google_id

        self.is_admin = bool(is_admin)
        self._is_active = bool(is_active)

    @property
    def is_active(self):

        return self._is_active
