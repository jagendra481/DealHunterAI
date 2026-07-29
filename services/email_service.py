import smtplib

from email.message import EmailMessage

from config.settings import (
    MAIL_EMAIL,
    MAIL_PASSWORD,
    MAIL_HOST,
    MAIL_PORT
)


class EmailService:

    # ==========================================================
    # SEND OTP EMAIL
    # ==========================================================

    @classmethod
    def send_registration_otp(
        cls,
        email,
        name,
        otp
    ):

        message = EmailMessage()

        message["Subject"] = (
            "Verify your DealHunterAI account"
        )

        message["From"] = (
            f"DealHunterAI <{MAIL_EMAIL}>"
        )

        message["To"] = email

        message.set_content(
            f"""
Hello {name},

Your DealHunterAI verification code is:

{otp}

This code expires in 10 minutes.

If you did not create a DealHunterAI account,
you can ignore this email.

DealHunterAI
Smarter price tracking. Better buying decisions.
"""
        )

        message.add_alternative(
            f"""
<!DOCTYPE html>

<html>

<body style="
    margin:0;
    padding:0;
    background:#f8fafc;
    font-family:Arial,sans-serif;
">

    <div style="
        max-width:600px;
        margin:40px auto;
        padding:20px;
    ">

        <div style="
            background:#ffffff;
            border-radius:18px;
            padding:40px;
            box-shadow:0 10px 30px rgba(0,0,0,0.08);
        ">

            <h1 style="
                color:#2563eb;
                text-align:center;
                margin-bottom:10px;
            ">
                🚀 DealHunterAI
            </h1>

            <p style="
                text-align:center;
                color:#64748b;
            ">
                Smarter price tracking.
                Better buying decisions.
            </p>

            <hr style="
                border:none;
                border-top:1px solid #e5e7eb;
                margin:30px 0;
            ">

            <h2 style="color:#1f2937;">
                Verify your email
            </h2>

            <p style="color:#64748b;">
                Hello {name},
            </p>

            <p style="color:#64748b;">
                Use the verification code below
                to complete your DealHunterAI
                registration.
            </p>

            <div style="
                background:#eff6ff;
                border-radius:14px;
                padding:25px;
                text-align:center;
                margin:30px 0;
            ">

                <div style="
                    font-size:38px;
                    font-weight:bold;
                    letter-spacing:10px;
                    color:#2563eb;
                ">
                    {otp}
                </div>

            </div>

            <p style="
                color:#64748b;
                text-align:center;
            ">
                This code expires in
                <strong>10 minutes</strong>.
            </p>

            <p style="
                color:#94a3b8;
                font-size:13px;
                margin-top:30px;
            ">
                If you did not create a
                DealHunterAI account, you can
                safely ignore this email.
            </p>

        </div>

        <p style="
            text-align:center;
            color:#94a3b8;
            font-size:13px;
            margin-top:20px;
        ">
            © DealHunterAI
        </p>

    </div>

</body>

</html>
""",
            subtype="html"
        )

        try:

            with smtplib.SMTP(
                MAIL_HOST,
                MAIL_PORT,
                timeout=20
            ) as server:

                server.ehlo()

                server.starttls()

                server.ehlo()

                server.login(
                    MAIL_EMAIL,
                    MAIL_PASSWORD
                )

                server.send_message(
                    message
                )

        except (
            smtplib.SMTPException,
            OSError
        ) as error:

            print(
                "\n❌ EMAIL SMTP ERROR:",
                repr(error)
            )

            raise Exception(
                f"Unable to send verification email: {error}"
            ) from error

    # ==========================================================
    # SEND TARGET PRICE ALERT EMAIL
    # ==========================================================

    @classmethod
    def send_target_price_alert(cls, email, name, product, target_price):
        if not email or "@" not in email:
            return

        product_name = getattr(product, "name", product.get("name") if isinstance(product, dict) else "Tracked Product")
        current_price = float(getattr(product, "current_price", product.get("current_price") if isinstance(product, dict) else 0) or 0)
        image_url = getattr(product, "image", product.get("image") if isinstance(product, dict) else "")
        buy_url = getattr(product, "affiliate_url", None) or getattr(product, "product_url", None) or (product.get("affiliate_url") if isinstance(product, dict) else product.get("product_url"))

        target_price = float(target_price or 0)

        message = EmailMessage()
        message["Subject"] = f"🎯 Target Price Reached! {product_name[:35]}..."
        message["From"] = f"DealHunterAI <{MAIL_EMAIL}>"
        message["To"] = email

        message.set_content(
            f"Hello {name},\n\n"
            f"Great news! Your tracked product '{product_name}' has hit your target price!\n\n"
            f"Current Price: ₹{current_price:,.2f}\n"
            f"Target Price: ₹{target_price:,.2f}\n\n"
            f"Buy Now: {buy_url}\n\n"
            f"- DealHunterAI Team"
        )

        message.add_alternative(
            f"""<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; background:#f8fafc; font-family: 'Inter', Arial, sans-serif;">
    <div style="max-width:600px; margin:30px auto; padding:20px;">
        <div style="background:#ffffff; border-radius:20px; padding:35px; box-shadow:0 15px 35px rgba(0,0,0,0.08); border:1px solid #e2e8f0;">
            <div style="text-align:center; margin-bottom:20px;">
                <span style="background:#dcfce7; color:#15803d; font-weight:bold; font-size:12px; padding:6px 14px; border-radius:20px; text-transform:uppercase; letter-spacing:1px;">
                    🎯 Target Price Alert Reached
                </span>
                <h1 style="color:#0f172a; margin-top:15px; margin-bottom:5px; font-size:24px;">🚀 DealHunterAI</h1>
            </div>
            
            <hr style="border:none; border-top:1px solid #f1f5f9; margin:20px 0;">

            <p style="color:#334155; font-size:16px; margin-bottom:20px;">
                Hello <strong>{name}</strong>,
            </p>

            <p style="color:#475569; font-size:15px; line-height:1.6;">
                Great news! A product on your watchlist has officially dropped to or below your target price.
            </p>

            <!-- Product Card -->
            <div style="background:#f8fafc; border-radius:16px; padding:20px; margin:25px 0; border:1px solid #e2e8f0; text-align:center;">
                {'<img src="' + image_url + '" alt="" style="max-width:140px; max-height:140px; object-fit:contain; margin-bottom:15px; border-radius:8px;">' if image_url else ''}
                <h3 style="color:#0f172a; font-size:16px; margin-top:0; margin-bottom:15px; line-height:1.4;">
                    {product_name}
                </h3>
                <div style="display:inline-block; background:#ffffff; padding:12px 25px; border-radius:12px; border:1px solid #cbd5e1; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                    <span style="color:#64748b; font-size:13px; display:block;">Current Price</span>
                    <span style="color:#16a34a; font-size:26px; font-weight:800;">₹{current_price:,.2f}</span>
                    <div style="color:#64748b; font-size:12px; margin-top:4px;">Target Price: ₹{target_price:,.2f}</div>
                </div>
            </div>

            <!-- Call to Action -->
            <div style="text-align:center; margin:30px 0;">
                <a href="{buy_url}" style="background:linear-gradient(135deg, #2563eb, #1d4ed8); color:#ffffff; font-weight:bold; text-decoration:none; padding:14px 32px; border-radius:12px; display:inline-block; font-size:16px; box-shadow:0 8px 20px rgba(37,99,235,0.3);">
                    🛒 Buy Now on Store
                </a>
            </div>

            <p style="color:#94a3b8; font-size:12px; text-align:center; margin-top:30px;">
                You received this alert because you enabled Target Price Notifications on DealHunterAI.
            </p>
        </div>
    </div>
</body>
</html>""",
            subtype="html"
        )

        cls._send(message)

    # ==========================================================
    # SEND PRICE DROP ALERT EMAIL
    # ==========================================================

    @classmethod
    def send_price_drop_alert(cls, email, name, product, old_price, new_price, drop_percent=0):
        if not email or "@" not in email:
            return

        product_name = getattr(product, "name", product.get("name") if isinstance(product, dict) else "Tracked Product")
        old_price = float(old_price or 0)
        new_price = float(new_price or 0)
        image_url = getattr(product, "image", product.get("image") if isinstance(product, dict) else "")
        buy_url = getattr(product, "affiliate_url", None) or getattr(product, "product_url", None) or (product.get("affiliate_url") if isinstance(product, dict) else product.get("product_url"))

        savings = max(0, old_price - new_price)

        message = EmailMessage()
        message["Subject"] = f"📉 Price Drop Alert! {product_name[:35]}..."
        message["From"] = f"DealHunterAI <{MAIL_EMAIL}>"
        message["To"] = email

        message.set_content(
            f"Hello {name},\n\n"
            f"Price Drop Detected for '{product_name}'!\n\n"
            f"Old Price: ₹{old_price:,.2f}\n"
            f"New Price: ₹{new_price:,.2f} (Save ₹{savings:,.2f})\n\n"
            f"Buy Now: {buy_url}\n\n"
            f"- DealHunterAI Team"
        )

        message.add_alternative(
            f"""<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; background:#f8fafc; font-family: 'Inter', Arial, sans-serif;">
    <div style="max-width:600px; margin:30px auto; padding:20px;">
        <div style="background:#ffffff; border-radius:20px; padding:35px; box-shadow:0 15px 35px rgba(0,0,0,0.08); border:1px solid #e2e8f0;">
            <div style="text-align:center; margin-bottom:20px;">
                <span style="background:#dbeafe; color:#1e40af; font-weight:bold; font-size:12px; padding:6px 14px; border-radius:20px; text-transform:uppercase; letter-spacing:1px;">
                    📉 Price Drop Detected
                </span>
                <h1 style="color:#0f172a; margin-top:15px; margin-bottom:5px; font-size:24px;">🚀 DealHunterAI</h1>
            </div>
            
            <hr style="border:none; border-top:1px solid #f1f5f9; margin:20px 0;">

            <p style="color:#334155; font-size:16px; margin-bottom:20px;">
                Hello <strong>{name}</strong>,
            </p>

            <p style="color:#475569; font-size:15px; line-height:1.6;">
                A product you are tracking just dropped in price!
            </p>

            <div style="background:#f8fafc; border-radius:16px; padding:20px; margin:25px 0; border:1px solid #e2e8f0; text-align:center;">
                {'<img src="' + image_url + '" alt="" style="max-width:140px; max-height:140px; object-fit:contain; margin-bottom:15px; border-radius:8px;">' if image_url else ''}
                <h3 style="color:#0f172a; font-size:16px; margin-top:0; margin-bottom:15px; line-height:1.4;">
                    {product_name}
                </h3>
                <div style="display:inline-block; background:#ffffff; padding:12px 25px; border-radius:12px; border:1px solid #cbd5e1; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
                    <span style="color:#94a3b8; font-size:13px; text-decoration:line-through;">Original: ₹{old_price:,.2f}</span>
                    <div style="color:#2563eb; font-size:26px; font-weight:800;">₹{new_price:,.2f}</div>
                    <div style="color:#16a34a; font-size:12px; font-weight:bold; margin-top:4px;">Save ₹{savings:,.2f}</div>
                </div>
            </div>

            <div style="text-align:center; margin:30px 0;">
                <a href="{buy_url}" style="background:linear-gradient(135deg, #2563eb, #1d4ed8); color:#ffffff; font-weight:bold; text-decoration:none; padding:14px 32px; border-radius:12px; display:inline-block; font-size:16px; box-shadow:0 8px 20px rgba(37,99,235,0.3);">
                    🛒 View Deal & Buy Now
                </a>
            </div>
        </div>
    </div>
</body>
</html>""",
            subtype="html"
        )

        cls._send(message)

    @classmethod
    def _send(cls, message):
        try:
            with smtplib.SMTP(MAIL_HOST, MAIL_PORT, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(MAIL_EMAIL, MAIL_PASSWORD)
                server.send_message(message)
                print(f"[EmailService Success] Gmail Notification Sent to {message['To']}")
        except (smtplib.SMTPException, OSError) as error:
            print("[EmailService Error] EMAIL SMTP ERROR:", repr(error))


