import threading
from functools import wraps

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import login_required, current_user, login_user


from database.database import Database
from engine.deal_engine import DealEngine
from engine.product_service import ProductService


from services.user_service import UserService


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("Administrator authentication required. Please enter admin email and password.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


def register_admin_routes(app):

    # ==========================================================
    # ADMIN LOGIN ROUTE
    # ==========================================================
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if current_user.is_authenticated and getattr(current_user, "is_admin", False):
            return redirect(url_for("admin_dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "").strip()

            service = UserService()
            try:
                # Master Admin Credential Override & Auto-Heal for Azure
                if email == "jagendra481@gmail.com" and password == "jagendra@123":
                    from werkzeug.security import generate_password_hash
                    h = generate_password_hash("jagendra@123")
                    
                    user_row = service.db.get_user_by_email("jagendra481@gmail.com")
                    if not user_row:
                        user_id = service.db.add_google_user("Jagendra Singh", "jagendra481@gmail.com", "admin-master")
                        user_row = service.db.get_user_by_id(user_id)

                    service.db.cursor.execute(
                        "UPDATE users SET password_hash = ?, is_admin = 1, is_active = 1 WHERE email = ?",
                        (h, "jagendra481@gmail.com")
                    )
                    service.db.connection.commit()

                    user_row = service.db.get_user_by_email("jagendra481@gmail.com")
                    user = service._row_to_user(user_row)
                    login_user(user)
                    flash("Admin Authentication Successful! Welcome to Admin Portal.", "success")
                    return redirect(url_for("admin_dashboard"))

                user = service.login(email, password)
                if user and user.is_admin:
                    login_user(user)
                    flash("Admin Authentication Successful! Welcome to Admin Portal.", "success")
                    return redirect(url_for("admin_dashboard"))
                elif user and not user.is_admin:
                    flash("This account does not have Administrator privileges.", "danger")
                else:
                    flash("Invalid admin email or password.", "danger")
            finally:
                service.close()

        return render_template("admin/login.html")



    # ==========================================================
    # ADMIN DASHBOARD OVERVIEW
    # ==========================================================
    @app.route("/admin")
    @admin_required
    def admin_dashboard():
        db = Database()
        try:
            stats = db.get_admin_stats()
            recent_scans = db.get_recent_scan_runs(limit=5)
            recent_users = db.get_all_users_admin()[:5]
            recent_products = db.get_all_global_products_admin()[:5]

            return render_template(
                "admin/dashboard.html",
                stats=stats,
                recent_scans=recent_scans,
                recent_users=recent_users,
                recent_products=recent_products
            )
        finally:
            db.close()

    # ==========================================================
    # USER MANAGEMENT
    # ==========================================================
    @app.route("/admin/users")
    @admin_required
    def admin_users():
        search_query = request.args.get("q", "").strip()
        db = Database()
        try:
            users = db.get_all_users_admin(search=search_query)
            return render_template(
                "admin/users.html",
                users=users,
                search_query=search_query
            )
        finally:
            db.close()

    @app.route("/admin/users/<int:user_id>/toggle-status", methods=["POST"])
    @admin_required
    def admin_toggle_user_status(user_id):
        if current_user.id == user_id:
            flash("You cannot block your own active account.", "warning")
            return redirect(url_for("admin_users"))

        db = Database()
        try:
            new_status = db.toggle_user_active_status(user_id)
            status_text = "activated" if new_status else "blocked"
            flash(f"User account successfully {status_text}.", "success")
        except Exception as error:
            flash(str(error), "danger")
        finally:
            db.close()

        return redirect(url_for("admin_users"))

    @app.route("/admin/users/<int:user_id>/toggle-admin", methods=["POST"])
    @admin_required
    def admin_toggle_user_admin(user_id):
        if current_user.id == user_id:
            flash("You cannot revoke your own admin rights.", "warning")
            return redirect(url_for("admin_users"))

        db = Database()
        try:
            new_admin = db.toggle_user_admin_status(user_id)
            role_text = "granted Administrator role" if new_admin else "revoked Administrator role"
            flash(f"User successfully {role_text}.", "success")
        except Exception as error:
            flash(str(error), "danger")
        finally:
            db.close()

        return redirect(url_for("admin_users"))

    # ==========================================================
    # GLOBAL PRODUCT AUDIT & CONTROL
    # ==========================================================
    @app.route("/admin/products")
    @admin_required
    def admin_products():
        search_query = request.args.get("q", "").strip()
        db = Database()
        try:
            products = db.get_all_global_products_admin(search=search_query)
            return render_template(
                "admin/products.html",
                products=products,
                search_query=search_query
            )
        finally:
            db.close()

    @app.route("/admin/products/<int:product_id>/refresh", methods=["POST"])
    @admin_required
    def admin_refresh_product(product_id):
        service = ProductService()
        try:
            product = service.get_product_by_id(product_id)
            if not product:
                flash("Product not found.", "danger")
                return redirect(url_for("admin_products"))

            service.refresh_product_metadata(product_id, product["user_id"])
            flash(f"Refreshed metadata for '{product['name']}'.", "success")
        except Exception as error:
            flash(f"Failed to refresh product: {error}", "danger")
        finally:
            service.close()

        return redirect(url_for("admin_products"))

    @app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
    @admin_required
    def admin_delete_product(product_id):
        db = Database()
        try:
            db.delete_product(product_id)
            flash("Product successfully removed from system.", "success")
        except Exception as error:
            flash(f"Failed to delete product: {error}", "danger")
        finally:
            db.close()

        return redirect(url_for("admin_products"))

    # ==========================================================
    # SCANNER & ENGINE DIAGNOSTICS
    # ==========================================================
    @app.route("/admin/scanner")
    @admin_required
    def admin_scanner():
        db = Database()
        try:
            scans = db.get_recent_scan_runs(limit=50)
            stats = db.get_admin_stats()
            return render_template(
                "admin/scanner.html",
                scans=scans,
                stats=stats
            )
        finally:
            db.close()

    @app.route("/admin/scanner/run", methods=["POST"])
    @admin_required
    def admin_trigger_scan():
        def run_background_scan():
            try:
                engine = DealEngine()
                engine.run()
            except Exception as e:
                print("ADMIN SCANNER ERROR:", e)

        thread = threading.Thread(target=run_background_scan, daemon=True)
        thread.start()

        flash("Manual Price Scanning Engine triggered successfully in background.", "success")
        return redirect(url_for("admin_scanner"))
