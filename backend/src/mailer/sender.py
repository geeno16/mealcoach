import logging
import os
from email.message import EmailMessage

logger = logging.getLogger(__name__)

_MAIL_BACKEND = os.getenv("MAIL_BACKEND", "console")
_SMTP_HOST = os.getenv("SMTP_HOST")
_SMTP_PORT = os.getenv("SMTP_PORT")
_SMTP_USER = os.getenv("SMTP_USER")
_SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
_SMTP_FROM = os.getenv("SMTP_FROM")

if _MAIL_BACKEND == "smtp" and not all(
    [_SMTP_HOST, _SMTP_PORT, _SMTP_USER, _SMTP_PASSWORD, _SMTP_FROM]
):
    raise RuntimeError(
        "MAIL_BACKEND=smtp requires SMTP_HOST, SMTP_PORT, SMTP_USER, "
        "SMTP_PASSWORD, SMTP_FROM"
    )


async def send_verification_code(email: str, code: str) -> None:
    subject = "Mealcoach: подтверждение почты"
    body = (
        f"Код для подтверждения почты: {code}\nОн скоро истечёт."
    )

    if _MAIL_BACKEND == "console":
        logger.info("Verification code for %s: %s", email, code)
        return

    import aiosmtplib

    message = EmailMessage()
    message["From"] = _SMTP_FROM
    message["To"] = email
    message["Subject"] = subject
    message.set_content(body)
    assert _SMTP_PORT

    await aiosmtplib.send(
        message,
        hostname=_SMTP_HOST,
        port=int(_SMTP_PORT),
        username=_SMTP_USER,
        password=_SMTP_PASSWORD,
        start_tls=True,
    )
