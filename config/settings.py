import os

from dotenv import load_dotenv


load_dotenv()


# ==========================================================
# HELPER
# ==========================================================

def get_required_env(name):

    value = os.getenv(name)

    if not value:

        raise ValueError(
            f"{name} not found in environment variables"
        )

    return value


# ==========================================================
# TELEGRAM
# ==========================================================

BOT_TOKEN = get_required_env(
    "BOT_TOKEN"
)

CHAT_ID = get_required_env(
    "CHAT_ID"
)


# ==========================================================
# AMAZON / RAINFOREST
# ==========================================================

RAINFOREST_API_KEY = get_required_env(
    "RAINFOREST_API_KEY"
)


# ==========================================================
# EMAIL / OTP
# ==========================================================

MAIL_EMAIL = get_required_env(
    "MAIL_EMAIL"
)

MAIL_PASSWORD = get_required_env(
    "MAIL_PASSWORD"
)

MAIL_HOST = os.getenv(
    "MAIL_HOST",
    "smtp.gmail.com"
)

MAIL_PORT = int(
    os.getenv(
        "MAIL_PORT",
        "587"
    )
)


# ==========================================================
# GOOGLE OAUTH
# ==========================================================

GOOGLE_CLIENT_ID = get_required_env(
    "GOOGLE_CLIENT_ID"
)

GOOGLE_CLIENT_SECRET = get_required_env(
    "GOOGLE_CLIENT_SECRET"
)


# ==========================================================
# DATABASE
# ==========================================================

DATABASE_NAME = "products.db"

RAILWAY_VOLUME_MOUNT_PATH = os.getenv(
    "RAILWAY_VOLUME_MOUNT_PATH"
)


if RAILWAY_VOLUME_MOUNT_PATH:

    DATABASE_DIRECTORY = (
        RAILWAY_VOLUME_MOUNT_PATH
    )

else:

    DATABASE_DIRECTORY = "data"


os.makedirs(
    DATABASE_DIRECTORY,
    exist_ok=True
)


DATABASE_PATH = os.path.join(
    DATABASE_DIRECTORY,
    DATABASE_NAME
)


# ==========================================================
# SCHEDULER
# ==========================================================

CHECK_INTERVAL_MINUTES = int(
    os.getenv(
        "CHECK_INTERVAL_MINUTES",
        "60"
    )
)
