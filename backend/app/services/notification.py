import aiosmtplib
from email.message import EmailMessage
from app.config import settings

async def send_alert_email(subject: str, body: str) -> bool:
    if not settings.smtp_host or not settings.alert_to_emails:
        return False
    msg = EmailMessage()
    msg["From"] = settings.alert_from_email
    msg["To"] = ", ".join(settings.alert_to_emails)
    msg["Subject"] = f"[HomeLab] {subject}"
    msg.set_content(body)
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_pass or None,
            start_tls=True,
        )
        return True
    except Exception:
        return False
