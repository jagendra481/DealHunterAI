from flask import redirect, url_for, flash
from flask_login import login_required, logout_user


def register_logout_route(app):

   
    @login_required
    def logout():

        logout_user()

        flash(
            "Logged out successfully!",
            "success"
        )

        return redirect(url_for("login"))
