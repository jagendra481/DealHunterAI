from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from authlib.integrations.flask_client import OAuth

from config.settings import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET
)

from services.user_service import UserService
from services.email_service import EmailService


oauth = OAuth()


def register_auth_routes(app):

    oauth.init_app(app)

    google = oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=(
            "https://accounts.google.com/"
            ".well-known/openid-configuration"
        ),
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    # ==========================================================
    # REGISTER
    # ==========================================================

    @app.route(
        "/register",
        methods=["GET", "POST"]
    )
    def register():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        if request.method == "POST":

            service = UserService()

            try:

                name = request.form.get(
                    "name",
                    ""
                ).strip()

                email = request.form.get(
                    "email",
                    ""
                ).strip().lower()

                password = request.form.get(
                    "password",
                    ""
                )

                otp = service.start_registration(
                    name,
                    email,
                    password
                )

                EmailService.send_registration_otp(
                    email,
                    name,
                    otp
                )

                session[
                    "pending_registration_email"
                ] = email

                flash(
                    "Verification code sent to your email.",
                    "success"
                )

                return redirect(
                    url_for("verify_otp")
                )

            except Exception as error:

                flash(
                    str(error),
                    "danger"
                )

            finally:

                service.close()

        return render_template(
            "register.html"
        )

    # ==========================================================
    # VERIFY OTP
    # ==========================================================

    @app.route(
        "/verify-otp",
        methods=["GET", "POST"]
    )
    def verify_otp():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        email = session.get(
            "pending_registration_email"
        )

        if not email:

            flash(
                "Please start registration first.",
                "warning"
            )

            return redirect(
                url_for("register")
            )

        if request.method == "POST":

            service = UserService()

            try:

                otp = request.form.get(
                    "otp",
                    ""
                ).strip()

                if not otp:

                    raise Exception(
                        "Please enter the verification code."
                    )

                user = (
                    service.verify_registration_otp(
                        email,
                        otp
                    )
                )

                if user is None:

                    raise Exception(
                        "Unable to create your account."
                    )

                session.pop(
                    "pending_registration_email",
                    None
                )

                login_user(user)

                flash(
                    "Email verified successfully. "
                    "Welcome to DealHunterAI!",
                    "success"
                )

                return redirect(
                    url_for("dashboard")
                )

            except Exception as error:

                flash(
                    str(error),
                    "danger"
                )

            finally:

                service.close()

        return render_template(
            "verify_otp.html",
            email=email
        )

    # ==========================================================
    # RESEND OTP
    # ==========================================================

    @app.route(
        "/resend-otp",
        methods=["POST"]
    )
    def resend_otp():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        email = session.get(
            "pending_registration_email"
        )

        if not email:

            flash(
                "Registration session not found.",
                "warning"
            )

            return redirect(
                url_for("register")
            )

        service = UserService()

        try:

            pending = (
                service.db.get_pending_registration(
                    email
                )
            )

            if pending is None:

                raise Exception(
                    "Registration session not found. "
                    "Please register again."
                )

            otp = service.resend_registration_otp(
                email
            )

            EmailService.send_registration_otp(
                pending["email"],
                pending["name"],
                otp
            )

            flash(
                "A new verification code has been sent.",
                "success"
            )

        except Exception as error:

            flash(
                str(error),
                "danger"
            )

        finally:

            service.close()

        return redirect(
            url_for("verify_otp")
        )

    # ==========================================================
    # LOGIN
    # ==========================================================

    @app.route(
        "/login",
        methods=["GET", "POST"]
    )
    def login():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        if request.method == "POST":

            service = UserService()

            try:

                user = service.login(
                    request.form.get(
                        "email",
                        ""
                    ),
                    request.form.get(
                        "password",
                        ""
                    )
                )

                if user:

                    login_user(user)

                    flash(
                        "Login Successful!",
                        "success"
                    )

                    return redirect(
                        url_for("dashboard")
                    )

                flash(
                    "Invalid Email or Password",
                    "danger"
                )

            finally:

                service.close()

        return render_template(
            "login.html"
        )

    # ==========================================================
    # GOOGLE LOGIN
    # ==========================================================

    @app.route("/auth/google")
    def google_login():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        redirect_uri = url_for(
            "google_callback",
            _external=True
        )

        return google.authorize_redirect(
            redirect_uri
        )

    # ==========================================================
    # GOOGLE CALLBACK
    # ==========================================================

    @app.route("/auth/google/callback")
    def google_callback():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        service = UserService()

        try:

            token = google.authorize_access_token()

            user_info = token.get(
                "userinfo"
            )

            if not user_info:

                raise Exception(
                    "Unable to read Google account information."
                )

            if not user_info.get(
                "email_verified"
            ):

                raise Exception(
                    "Google email is not verified."
                )

            user = service.google_login(
                user_info.get(
                    "name",
                    ""
                ),
                user_info.get(
                    "email",
                    ""
                ),
                user_info.get(
                    "sub",
                    ""
                )
            )

            login_user(user)

            session.pop(
                "pending_registration_email",
                None
            )

            flash(
                "Successfully signed in with Google!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as error:

            print(
                "GOOGLE LOGIN ERROR:",
                repr(error)
            )

            flash(
                "Google sign-in failed. "
                "Please try again.",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        finally:

            service.close()

    # ==========================================================
    # LOGOUT
    # ==========================================================

    @app.route("/logout")
    @login_required
    def logout():

        logout_user()

        session.pop(
            "pending_registration_email",
            None
        )

        flash(
            "Logged out successfully.",
            "success"
        )

        return redirect(
            url_for("login")
        )
