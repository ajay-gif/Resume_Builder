import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from flask import current_app

logger = logging.getLogger(__name__)

def build_reset_email_html(user_name, reset_url):
    """Generates an aesthetic, responsive HTML email matching the Stitch design system."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f6faff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #141d23; line-height: 1.6;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f6faff; padding: 40px 15px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" max-width="560" style="max-width: 560px; background-color: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 18px rgba(35, 44, 51, 0.08); border: 1px solid #dae4ed;">
                    <!-- Brand Top Bar -->
                    <tr>
                        <td style="background-color: #232C33; padding: 22px 32px; border-bottom: 3px solid #5A7D7C;">
                            <table role="presentation" width="100%">
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
                                            🎓 ResumePortal
                                        </h1>
                                        <span style="font-size: 11px; color: #c4eae8; font-weight: 500;">Academic & Career Nexus</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 32px 32px 24px 32px;">
                            <h2 style="margin: 0 0 14px 0; font-size: 22px; font-weight: 700; color: #141d23;">
                                Password Reset Request
                            </h2>
                            <p style="margin: 0 0 16px 0; font-size: 15px; color: #414848;">
                                Hello {user_name or 'Student'},
                            </p>
                            <p style="margin: 0 0 24px 0; font-size: 14px; color: #414848; line-height: 1.6;">
                                We received a request to reset the password associated with your account on <strong>ResumePortal</strong>. Click the button below to choose a new password:
                            </p>

                            <!-- CTA Button -->
                            <table role="presentation" cellspacing="0" cellpadding="0" style="margin: 28px 0;">
                                <tr>
                                    <td align="center" style="border-radius: 8px; background-color: #5A7D7C;">
                                        <a href="{reset_url}" target="_blank" style="display: inline-block; padding: 14px 28px; font-size: 14px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 8px; letter-spacing: 0.3px;">
                                            Reset My Password →
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Expiration notice -->
                            <div style="background-color: #ebf5fe; border-left: 4px solid #436371; padding: 12px 16px; border-radius: 6px; margin: 24px 0; font-size: 13px; color: #141d23;">
                                ⏱️ <strong>Security Notice:</strong> This reset link will safely expire in <strong>60 minutes</strong>.
                            </div>

                            <p style="margin: 0 0 8px 0; font-size: 13px; color: #717978;">
                                If the button above doesn't work, copy and paste this URL into your browser:
                            </p>
                            <p style="margin: 0 0 24px 0; font-size: 12px; word-break: break-all; color: #436371;">
                                <a href="{reset_url}" style="color: #416463; text-decoration: underline;">{reset_url}</a>
                            </p>

                            <hr style="border: none; border-top: 1px solid #e0e9f3; margin: 24px 0;">

                            <p style="margin: 0; font-size: 12px; color: #717978;">
                                If you did not request a password reset, please disregard this email. Your password will remain unchanged and your account is secure.
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f6faff; padding: 18px 32px; border-top: 1px solid #dae4ed; text-align: center; font-size: 12px; color: #717978;">
                            © Academic Career Nexus • Student Resume Portal
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

def _send_via_resend_api(to_email, user_name, reset_url):
    """
    Sends email using Resend HTTPS REST API (https://resend.com).
    Perfect for testing without purchasing a custom domain by sending via onboarding@resend.dev.
    """
    api_key = current_app.config.get('RESEND_API_KEY', '').strip()
    from_address = (current_app.config.get('RESEND_FROM_ADDRESS') or current_app.config.get('MAIL_FROM_ADDRESS', 'onboarding@resend.dev')).strip()
    from_name = current_app.config.get('MAIL_FROM_NAME', 'ResumePortal Academic Nexus').strip()

    if not api_key:
        return False, "RESEND_API_KEY is not configured."

    auth_header = api_key
    if not auth_header.startswith("Bearer "):
        auth_header = f"Bearer {api_key}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": auth_header
    }

    html_content = build_reset_email_html(user_name, reset_url)
    text_content = (
        f"Hello {user_name or 'Student'},\n\n"
        f"We received a request to reset your password for your ResumePortal account.\n"
        f"Click the link below to set a new password:\n{reset_url}\n\n"
        f"This link expires in 60 minutes.\n"
        f"If you did not request this, you can safely ignore this email."
    )

    # Resend sender formatting: "Display Name <email@domain.com>" or "email@domain.com"
    formatted_from = f"{from_name} <{from_address}>" if from_name and "<" not in from_address else from_address

    payload = {
        "from": formatted_from,
        "to": [to_email],
        "subject": "Reset Your ResumePortal Password",
        "html": html_content,
        "text": text_content
    }

    resend_url = current_app.config.get('RESEND_URL', 'https://api.resend.com/emails').strip()

    try:
        response = requests.post(resend_url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            current_app.logger.info(f"Password reset email dispatched to {to_email} via Resend API.")
            return True, "Password reset email sent successfully via Resend API."
        else:
            err_msg = f"Resend API error (Status {response.status_code}): {response.text}"
            current_app.logger.error(err_msg)
            return False, err_msg
    except Exception as e:
        err_msg = f"Resend API communication error: {str(e)}"
        current_app.logger.error(err_msg)
        return False, err_msg


def _send_via_zeptomail_api(to_email, user_name, reset_url):
    """
    Sends email using Zoho ZeptoMail HTTPS REST API.
    Used once a custom domain is verified in Zoho ZeptoMail.
    """
    api_key = current_app.config.get('ZEPTOMAIL_API_KEY', '').strip()
    zepto_url = current_app.config.get('ZEPTOMAIL_URL', 'https://api.zeptomail.in/v1.1/email').strip()
    from_address = current_app.config.get('MAIL_FROM_ADDRESS', 'noreply@studentresumes.app').strip()
    from_name = current_app.config.get('MAIL_FROM_NAME', 'ResumePortal Academic Nexus').strip()

    auth_header = api_key
    if not auth_header.startswith("Zoho-enczapikey"):
        auth_header = f"Zoho-enczapikey {api_key}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": auth_header
    }

    html_content = build_reset_email_html(user_name, reset_url)
    text_content = (
        f"Hello {user_name or 'Student'},\n\n"
        f"We received a request to reset your password for your ResumePortal account.\n"
        f"Click the link below to set a new password:\n{reset_url}\n\n"
        f"This link expires in 60 minutes.\n"
        f"If you did not request this, you can safely ignore this email."
    )

    payload = {
        "from": {
            "address": from_address,
            "name": from_name
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                    "name": user_name or "Student"
                }
            }
        ],
        "subject": "Reset Your ResumePortal Password",
        "htmlbody": html_content,
        "textbody": text_content
    }

    try:
        response = requests.post(zepto_url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            current_app.logger.info(f"Password reset email dispatched to {to_email} via ZeptoMail API.")
            return True, "Password reset email sent successfully via ZeptoMail API."
        else:
            err_msg = f"ZeptoMail API error (Status {response.status_code}): {response.text}"
            current_app.logger.error(err_msg)
            return False, err_msg
    except Exception as e:
        err_msg = f"ZeptoMail API communication error: {str(e)}"
        current_app.logger.error(err_msg)
        return False, err_msg


def _send_via_smtp(to_email, user_name, reset_url):
    """
    Sends email using SMTP with TLS/SSL.
    Compatible with Zoho ZeptoMail SMTP (smtp.zeptomail.in, Port 587/465, username: emailapikey).
    """
    smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.zeptomail.in').strip()
    smtp_port = current_app.config.get('SMTP_PORT', 587)
    smtp_user = current_app.config.get('SMTP_USERNAME', 'emailapikey').strip()
    smtp_password = (current_app.config.get('SMTP_PASSWORD') or current_app.config.get('ZEPTOMAIL_API_KEY', '')).strip()
    from_address = current_app.config.get('MAIL_FROM_ADDRESS', 'noreply@studentresumes.app').strip()
    from_name = current_app.config.get('MAIL_FROM_NAME', 'ResumePortal Academic Nexus').strip()
    use_tls = current_app.config.get('SMTP_USE_TLS', True)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Reset Your ResumePortal Password"
    msg['From'] = f"{from_name} <{from_address}>"
    msg['To'] = to_email

    text_content = (
        f"Hello {user_name or 'Student'},\n\n"
        f"We received a request to reset your password for your ResumePortal account.\n"
        f"Click the link below to set a new password:\n{reset_url}\n\n"
        f"This link expires in 60 minutes.\n"
        f"If you did not request this, you can safely ignore this email."
    )
    html_content = build_reset_email_html(user_name, reset_url)

    msg.attach(MIMEText(text_content, 'plain'))
    msg.attach(MIMEText(html_content, 'html'))

    try:
        context = ssl.create_default_context()
        if smtp_port == 465:
            # SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=10) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(from_address, [to_email], msg.as_string())
        else:
            # STARTTLS (Port 587)
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                if use_tls:
                    server.starttls(context=context)
                server.login(smtp_user, smtp_password)
                server.sendmail(from_address, [to_email], msg.as_string())

        current_app.logger.info(f"Password reset email dispatched to {to_email} via SMTP.")
        return True, "Password reset email sent successfully via SMTP."
    except Exception as e:
        err_msg = f"SMTP transmission error: {str(e)}"
        current_app.logger.error(err_msg)
        return False, err_msg


def send_password_reset_email(to_email, user_name, reset_url):
    """
    Main dispatch controller for password reset emails.
    Supports:
      1. 'resend' (Resend API - default for testing without custom domain)
      2. 'zeptomail' (ZeptoMail API - for custom domain production)
      3. 'smtp' (SMTP TLS)
    Falls back gracefully to development console logging if credentials are missing or in test mode.
    """
    provider = current_app.config.get('EMAIL_PROVIDER', 'resend').lower()

    # If provider is not explicitly set or set to resend, check Resend API key
    resend_key = current_app.config.get('RESEND_API_KEY', '').strip()
    zepto_key = current_app.config.get('ZEPTOMAIL_API_KEY', '').strip()
    smtp_password = (current_app.config.get('SMTP_PASSWORD') or zepto_key).strip()

    is_testing = current_app.config.get('TESTING', False)
    has_resend_creds = bool(resend_key and 'test' not in resend_key.lower())
    has_zepto_creds = bool(zepto_key and 'test' not in zepto_key.lower())
    has_smtp_creds = bool(smtp_password and 'test' not in smtp_password.lower())

    # Fallback to console logging in development or testing without live keys
    if is_testing or (provider == 'resend' and not has_resend_creds) \
                  or (provider == 'zeptomail' and not has_zepto_creds) \
                  or (provider == 'smtp' and not has_smtp_creds):
        msg = f"[DEV / TEST MODE] Password reset email for {to_email} (Provider: {provider.upper()}). Reset link: {reset_url}"
        current_app.logger.info(msg)
        print(f"\n{'='*70}\n{msg}\n{'='*70}\n")
        return True, "Password reset instructions logged in development mode."

    if provider == 'resend':
        return _send_via_resend_api(to_email, user_name, reset_url)
    elif provider == 'zeptomail':
        return _send_via_zeptomail_api(to_email, user_name, reset_url)
    elif provider == 'smtp':
        return _send_via_smtp(to_email, user_name, reset_url)
    else:
        # Default fallback to Resend API
        return _send_via_resend_api(to_email, user_name, reset_url)
