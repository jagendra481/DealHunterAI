import secrets

from datetime import (
    datetime,
    timedelta
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.database import Database
from models.user import User


class UserService:

    OTP_EXPIRY_MINUTES = 10

    MAX_OTP_ATTEMPTS = 5

    def __init__(self):

        self.db = Database()

    # ==========================================================
    # START REGISTRATION
    # ==========================================================

    def start_registration(
        self,
        name,
        email,
        password
    ):

        name = name.strip()

        email = email.strip().lower()

        self._validate_registration(
            name,
            email,
            password
        )

        existing = self.db.get_user_by_email(
            email
        )

        if existing:

            raise Exception(
                "Email already registered."
            )

        password_hash = generate_password_hash(
            password
        )

        otp = self._generate_otp()

        otp_hash = generate_password_hash(
            otp
        )

        otp_expires_at = (
            datetime.now()
            + timedelta(
                minutes=self.OTP_EXPIRY_MINUTES
            )
        )

        self.db.save_pending_registration(
            name,
            email,
            password_hash,
            otp_hash,
            otp_expires_at
        )

        return otp

    # ==========================================================
    # VERIFY OTP
    # ==========================================================

    def verify_registration_otp(
        self,
        email,
        otp
    ):

        email = email.strip().lower()

        otp = str(otp).strip()

        pending = (
            self.db.get_pending_registration(
                email
            )
        )

        if pending is None:

            raise Exception(
                "Registration session not found. "
                "Please register again."
            )

        if pending["otp_attempts"] >= (
            self.MAX_OTP_ATTEMPTS
        ):

            self.db.delete_pending_registration(
                email
            )

            raise Exception(
                "Too many incorrect OTP attempts. "
                "Please register again."
            )

        expires_at = datetime.fromisoformat(
            str(
                pending["otp_expires_at"]
            )
        )

        if datetime.now() > expires_at:

            self.db.delete_pending_registration(
                email
            )

            raise Exception(
                "OTP has expired. "
                "Please register again."
            )

        if not check_password_hash(
            pending["otp_hash"],
            otp
        ):

            self.db.increment_otp_attempts(
                email
            )

            remaining_attempts = (
                self.MAX_OTP_ATTEMPTS
                - pending["otp_attempts"]
                - 1
            )

            raise Exception(
                "Invalid OTP. "
                f"{remaining_attempts} attempts remaining."
            )

        existing = self.db.get_user_by_email(
            email
        )

        if existing:

            self.db.delete_pending_registration(
                email
            )

            raise Exception(
                "Email already registered."
            )

        user = User(
            name=pending["name"],
            email=pending["email"],
            password_hash=pending["password_hash"]
        )

        self.db.add_user(
            user
        )

        self.db.delete_pending_registration(
            email
        )

        return self.login(
            email,
            None,
            password_hash=pending["password_hash"]
        )

    # ==========================================================
    # RESEND OTP
    # ==========================================================

    def resend_registration_otp(
        self,
        email
    ):

        email = email.strip().lower()

        pending = (
            self.db.get_pending_registration(
                email
            )
        )

        if pending is None:

            raise Exception(
                "Registration session not found. "
                "Please register again."
            )

        otp = self._generate_otp()

        otp_hash = generate_password_hash(
            otp
        )

        otp_expires_at = (
            datetime.now()
            + timedelta(
                minutes=self.OTP_EXPIRY_MINUTES
            )
        )

        self.db.save_pending_registration(
            pending["name"],
            pending["email"],
            pending["password_hash"],
            otp_hash,
            otp_expires_at
        )

        return otp

    # ==========================================================
    # REGISTER
    # ==========================================================

    def register(
        self,
        name,
        email,
        password
    ):

        return self.start_registration(
            name,
            email,
            password
        )

    # ==========================================================
    # PASSWORD LOGIN
    # ==========================================================

    def login(
        self,
        email,
        password=None,
        password_hash=None
    ):

        email = email.strip().lower()

        row = self.db.get_user_by_email(
            email
        )

        if row is None:

            return None

        if password_hash is not None:

            if row["password_hash"] != password_hash:

                return None

        else:

            if not row["password_hash"]:

                return None

            if not check_password_hash(
                row["password_hash"],
                password or ""
            ):

                return None

        return self._row_to_user(
            row
        )

    # ==========================================================
    # GOOGLE LOGIN
    # ==========================================================

    def google_login(
        self,
        name,
        email,
        google_id
    ):

        name = str(
            name or ""
        ).strip()

        email = str(
            email or ""
        ).strip().lower()

        google_id = str(
            google_id or ""
        ).strip()

        if not email:

            raise Exception(
                "Google account email was not received."
            )

        if not google_id:

            raise Exception(
                "Google account ID was not received."
            )

        google_user = (
            self.db.get_user_by_google_id(
                google_id
            )
        )

        if google_user:

            return self._row_to_user(
                google_user
            )

        existing = self.db.get_user_by_email(
            email
        )

        if existing:

            self.db.link_google_account(
                existing["id"],
                google_id
            )

            updated = self.db.get_user_by_id(
                existing["id"]
            )

            return self._row_to_user(
                updated
            )

        user_id = self.db.add_google_user(
            name or "DealHunter User",
            email,
            google_id
        )

        row = self.db.get_user_by_id(
            user_id
        )

        return self._row_to_user(
            row
        )

    # ==========================================================
    # GET USER
    # ==========================================================

    def get_user_by_id(
        self,
        user_id
    ):

        row = self.db.get_user_by_id(
            user_id
        )

        if row is None:

            return None

        return self._row_to_user(
            row
        )

    # ==========================================================
    # UPDATE SETTINGS
    # ==========================================================

    def update_settings(
        self,
        user_id,
        name,
        telegram_chat_id,
        telegram_notifications=True,
        target_price_alerts=True,
        deal_score_alerts=True,
        price_drop_alerts=True
    ):

        name = name.strip()

        telegram_chat_id = (
            telegram_chat_id.strip()
            if telegram_chat_id
            else ""
        )

        if not name:

            raise Exception(
                "Name cannot be empty."
            )

        self.db.update_user_settings(
            user_id,
            name,
            telegram_chat_id,
            telegram_notifications,
            target_price_alerts,
            deal_score_alerts,
            price_drop_alerts
        )

    # ==========================================================
    # VALIDATE REGISTRATION
    # ==========================================================

    @staticmethod
    def _validate_registration(
        name,
        email,
        password
    ):

        if not name:

            raise Exception(
                "Name cannot be empty."
            )

        if not email:

            raise Exception(
                "Email cannot be empty."
            )

        if "@" not in email:

            raise Exception(
                "Please enter a valid email address."
            )

        if len(password) < 6:

            raise Exception(
                "Password must contain at least "
                "6 characters."
            )

    # ==========================================================
    # GENERATE OTP
    # ==========================================================

    @staticmethod
    def _generate_otp():

        return str(
            secrets.randbelow(
                900000
            )
            + 100000
        )

    # ==========================================================
    # ROW TO USER
    # ==========================================================

    @staticmethod
    def _row_to_user(row):

        user = User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            telegram_chat_id=row["telegram_chat_id"],
            auth_provider=row["auth_provider"],
            google_id=row["google_id"],
            is_admin=bool(
                row["is_admin"]
            ),
            is_active=bool(
                row["is_active"]
            )
        )

        user.telegram_notifications = bool(
            row["telegram_notifications"]
        )

        user.target_price_alerts = bool(
            row["target_price_alerts"]
        )

        user.deal_score_alerts = bool(
            row["deal_score_alerts"]
        )

        user.price_drop_alerts = bool(
            row["price_drop_alerts"]
        )

        return user

    # ==========================================================
    # CLOSE
    # ==========================================================

    def close(self):

        self.db.close()
