from flask import Flask

from dashboard.routes import register_routes
from auth.auth_routes import register_auth_routes

app = Flask(__name__)

app.secret_key = "dealhunterai-secret"

register_routes(app)
register_auth_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
