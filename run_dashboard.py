import os

from flask import Flask
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

from dashboard.routes import register_routes
from auth.auth_routes import register_auth_routes
from auth.login_manager import login_manager


# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()


# ==========================================================
# CREATE FLASK APP
# ==========================================================

app = Flask(__name__)

# Trust Azure reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,
    x_host=1
)

# Always generate HTTPS external URLs
app.config["PREFERRED_URL_SCHEME"] = "https"


# ==========================================================
# SECURITY CONFIGURATION
# ==========================================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in .env")

app.config["SECRET_KEY"] = SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Optional but recommended when using HTTPS
app.config["SESSION_COOKIE_SECURE"] = True


# ==========================================================
# LOGIN MANAGER
# ==========================================================

login_manager.init_app(app)


# ==========================================================
# REGISTER ROUTES
# ==========================================================

register_routes(app)
register_auth_routes(app)


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)
