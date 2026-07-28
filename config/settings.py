import os

from dotenv import load_dotenv


load_dotenv()


# ==========================================================
# HELPER
# ==========================================================

def get_required_env(name):

    value = os.getenv(name)

    if not value:

        print(f"⚠️ Warning: {name} not found in environment variables")
        return ""

    return value.strip().strip('"').strip("'")




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

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    ""
).strip().strip('"').strip("'")

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET",
    ""
).strip().strip('"').strip("'")



# ==========================================================
# DATABASE
# ==========================================================

DATABASE_NAME = "products.db"

PERSISTENT_STORAGE_PATH = os.getenv("PERSISTENT_STORAGE_PATH")
RAILWAY_VOLUME_MOUNT_PATH = os.getenv("RAILWAY_VOLUME_MOUNT_PATH")

if PERSISTENT_STORAGE_PATH:
    DATABASE_DIRECTORY = PERSISTENT_STORAGE_PATH
elif RAILWAY_VOLUME_MOUNT_PATH:
    DATABASE_DIRECTORY = RAILWAY_VOLUME_MOUNT_PATH
elif os.path.exists("/home") and os.access("/home", os.W_OK):
    DATABASE_DIRECTORY = "/home/data"
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

EARNKARO_ID = os.getenv("EARNKARO_ID", "1554365").strip()
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "dealhunterai-21").strip()


