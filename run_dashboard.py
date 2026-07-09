from flask import Flask

from dashboard.routes import register_routes
from auth.auth_routes import register_auth_routes
from auth.logout import register_logout_route
from auth.login_manager import login_manager

app = Flask(__name__)

app.secret_key = "dealhunterai-secret"

login_manager.init_app(app)

register_routes(app)
register_auth_routes(app)
register_logout_route(app)

if __name__ == "__main__":
    app.run(debug=True)
