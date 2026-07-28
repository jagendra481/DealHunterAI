import os

from flask import Flask
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

from dashboard.routes import register_routes
from auth.auth_routes import register_auth_routes
from admin.admin_routes import register_admin_routes
from auth.login_manager import login_manager



# ==========================================================
# ENVIRONMENT
# ==========================================================

load_dotenv()


# ==========================================================
# CREATE FLASK APP
# ==========================================================

app = Flask(__name__)

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



# ==========================================================
# SECURITY CONFIGURATION
# ==========================================================

SECRET_KEY = os.getenv("SECRET_KEY", "dealhunterai_secret_key_production_2026_secure")
app.config["SECRET_KEY"] = SECRET_KEY


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Only enable SECURE cookies in production (HTTPS)
app.config["SESSION_COOKIE_SECURE"] = not (app.debug or os.getenv("FLASK_ENV") == "development")



# ==========================================================
# LOGIN MANAGER
# ==========================================================

login_manager.init_app(app)


# ==========================================================
# REGISTER ROUTES
# ==========================================================

register_routes(app)
register_auth_routes(app)
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

# Auto-start scheduler asynchronously in daemon thread to guarantee instantaneous WSGI import & prevent 503 errors
import threading
threading.Thread(target=_start_background_scheduler, daemon=True).start()



# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)

