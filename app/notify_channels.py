"""
GPA-ERP — Notification channels (email via SMTP).
All functions are no-ops if credentials are not configured.
Silent degradation: if SMTP not configured, in-app notification still works.
"""
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body_html: str, body_text: str | None = None) -> None:
    """
    Send an email via SMTP. No-op if SMTP_HOST is not configured.
    Runs synchronously — call from FastAPI BackgroundTasks for non-blocking behavior.
    """
    settings = get_settings()
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        return  # Not configured — silent no-op

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to_email

    if body_text:
        msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    try:
        if settings.SMTP_USE_TLS:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
                s.ehlo()
                s.starttls(context=ctx)
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                s.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                s.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
        logger.info("Email sent to %s: %s", to_email, subject)
    except Exception as exc:
        logger.warning("Email send failed to %s: %s", to_email, exc)
        # Never raise — email failure must not break the main flow


def build_notification_email(title: str, body: str, link: str, base_url: str = "http://localhost:3000") -> tuple[str, str]:
    """Build (html, text) email body for a notification."""
    full_link = f"{base_url}{link}" if link.startswith("/") else link
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;color:#1e293b">
      <div style="background:#0d9488;padding:16px 24px;border-radius:8px 8px 0 0">
        <span style="color:white;font-size:18px;font-weight:bold">GPA ERP</span>
      </div>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-top:none;padding:24px;border-radius:0 0 8px 8px">
        <h2 style="margin:0 0 12px;color:#1e293b;font-size:16px">{title}</h2>
        <p style="margin:0 0 20px;color:#475569;font-size:14px;line-height:1.6">{body}</p>
        <a href="{full_link}"
           style="display:inline-block;background:#0d9488;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-size:14px;font-weight:600">
          Lihat Detail &rarr;
        </a>
      </div>
      <p style="margin:16px 0 0;color:#94a3b8;font-size:11px;text-align:center">
        GPA Cost Control ERP &middot; Notifikasi otomatis, jangan balas email ini.
      </p>
    </div>
    """
    text = f"{title}\n\n{body}\n\nLink: {full_link}"
    return html, text
