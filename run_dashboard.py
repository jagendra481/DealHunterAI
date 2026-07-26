import os

from flask import Flask
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

from dashboard.routes import register_routes
from auth.auth_routes import register_auth_routes
<<<<<<< HEAD
from admin.admin_routes import register_admin_routes
from auth.login_manager import login_manager



=======
from auth.login_manager import login_manager


>>>>>>> d3c391c0d15ab8e49739e24f6dcecc07d72eba2f
# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()


# ==========================================================
# CREATE FLASK APP
# ==========================================================

app = Flask(__name__)

<<<<<<< HEAD
# Trust proxy headers on Azure / Nginx
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_port=1
)


# Configure scheme and OAuth transport for development vs production
if app.debug or os.getenv("FLASK_ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    app.config["PREFERRED_URL_SCHEME"] = os.getenv("PREFERRED_URL_SCHEME", "http")
else:
    app.config["PREFERRED_URL_SCHEME"] = os.getenv("PREFERRED_URL_SCHEME", "https")

=======
# Trust Azure reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,
    x_host=1
)

# Always generate HTTPS external URLs
app.config["PREFERRED_URL_SCHEME"] = "https"
>>>>>>> d3c391c0d15ab8e49739e24f6dcecc07d72eba2f


# ==========================================================
# SECURITY CONFIGURATION
# ==========================================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in .env")

app.config["SECRET_KEY"] = SECRET_KEY

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

<<<<<<< HEAD
# Only enable SECURE cookies in production (HTTPS)
app.config["SESSION_COOKIE_SECURE"] = not (app.debug or os.getenv("FLASK_ENV") == "development")

=======
# Optional but recommended when using HTTPS
app.config["SESSION_COOKIE_SECURE"] = True
>>>>>>> d3c391c0d15ab8e49739e24f6dcecc07d72eba2f


# ==========================================================
# LOGIN MANAGER
# ==========================================================

login_manager.init_app(app)


# ==========================================================
# REGISTER ROUTES
# ==========================================================

register_routes(app)
register_auth_routes(app)
<<<<<<< HEAD
register_admin_routes(app)



# ==========================================================
# BACKGROUND SCHEDULER & TELEGRAM LISTENER
# ==========================================================

def _start_background_scheduler():
    try:
        from scheduler.scheduler import DealScheduler
        scheduler = DealScheduler()
        scheduler.start()
        print("🚀 Auto-started 15-Minute DealScheduler in Gunicorn App Process")
    except Exception as err:
        print(f"⚠️ Scheduler startup warning: {err}")

# Auto-start scheduler in production / main process
_start_background_scheduler()
=======
>>>>>>> d3c391c0d15ab8e49739e24f6dcecc07d72eba2f


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)

