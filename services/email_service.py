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
