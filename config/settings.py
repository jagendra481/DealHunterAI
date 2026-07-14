import os

from dotenv import load_dotenv


load_dotenv()


# ==========================================================
# TELEGRAM
# ==========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")


# ==========================================================
# AMAZON / RAINFOREST
# ==========================================================

RAINFOREST_API_KEY = os.getenv(
    "RAINFOREST_API_KEY"
)


# ==========================================================
# EMAIL / OTP
# ==========================================================

MAIL_EMAIL = os.getenv("MAIL_EMAIL")

MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

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
# VALIDATION
# ==========================================================

if BOT_TOKEN is None:

    raise ValueError(
        "BOT_TOKEN not found in .env"
    )


if CHAT_ID is None:

    raise ValueError(
        "CHAT_ID not found in .env"
    )


if RAINFOREST_API_KEY is None:

    raise ValueError(
        "RAINFOREST_API_KEY not found in .env"
    )


if MAIL_EMAIL is None:

    raise ValueError(
        "MAIL_EMAIL not found in .env"
    )


if MAIL_PASSWORD is None:

    raise ValueError(
        "MAIL_PASSWORD not found in .env"
    )


# ==========================================================
# DATABASE
# ==========================================================

DATABASE_NAME = "products.db"

DATABASE_PATH = os.path.join(
    "data",
    DATABASE_NAME
)


# ==========================================================
# SCHEDULER
# ==========================================================

CHECK_INTERVAL_MINUTES = 60
GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID"
)

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET"
)


if not GOOGLE_CLIENT_ID:

    raise ValueError(
        "GOOGLE_CLIENT_ID not found in .env"
    )


if not GOOGLE_CLIENT_SECRET:

    raise ValueError(
        "GOOGLE_CLIENT_SECRET not found in .env"
    )

