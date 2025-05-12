import logging
from typing import List, Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM_ADDRESS,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="Teacherly AI",
    MAIL_STARTTLS=True, # Use STARTTLS
    MAIL_SSL_TLS=False, # Don't use implicit SSL/TLS if using STARTTLS
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True # Good practice to validate certs
)

fm = FastMail(conf)

async def send_email_async(subject: str, email_to: str, body: str):
    """
    Sends an email asynchronously.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAIL_FROM_ADDRESS]):
        logger.error("SMTP settings are not fully configured. Cannot send email.")
        # In a real app, you might want to raise an error or handle this differently
        return

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"
    )

    try:
        await fm.send_message(message)
        logger.info(f"Email sent successfully to {email_to} with subject '{subject}'")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}")
        # Depending on the context, you might want to raise an exception here
        # raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

# Example usage (for testing purposes, can be removed later)
# if __name__ == "__main__":
#     import asyncio
#     async def main():
#         await send_email_async(
#             subject="Test Email from Teacherly AI",
#             email_to="test_recipient@example.com", # Replace with a real test email
#             body="<h1>Hello!</h1><p>This is a test email sent asynchronously.</p>"
#         )
#     asyncio.run(main())