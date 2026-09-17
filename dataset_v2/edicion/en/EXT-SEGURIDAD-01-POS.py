"""Email client for loan due-date notices."""
import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.getenv("SMTP_HOST", "smtp.biblioteca.local")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_notice(recipient, book_title, due_date):
    """Sends a due-date notice to the user of the loan."""
    message = EmailMessage()
    message["Subject"] = "Your loan is about to expire"
    message["To"] = recipient
    message.set_content(f"The book '{book_title}' must be returned on {due_date}.")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)
