from flask import render_template, request, redirect, url_for, flash

from services.user_service import UserService


def register_auth_routes(app):

    @app.route("/register", methods=["GET", "POST"])
    def register():

        if request.method == "POST":

            try:

                service = UserService()

                service.register(
                    request.form["name"],
                    request.form["email"],
                    request.form["password"]
                )

                service.close()

                flash("Registration Successful!", "success")

                return redirect(url_for("login"))

            except Exception as e:

                flash(str(e), "danger")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if request.method == "POST":

            service = UserService()

            user = service.login(
                request.form["email"],
                request.form["password"]
            )

            service.close()

            if user:

                flash("Login Successful!", "success")

                return redirect(url_for("dashboard"))

            flash("Invalid Email or Password", "danger")

        return render_template("login.html")
