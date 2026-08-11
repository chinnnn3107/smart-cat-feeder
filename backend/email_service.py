import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST=os.getenv("SMTP_HOST")
SMTP_PORT=int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL=os.getenv("SMTP_EMAIL")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD")

def sendEmail(to_email, subject, body):
    message = EmailMessage()

    message["From"] = SMTP_HOST
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(message)

        print("Email sent successfully.")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Email authentication failed.")
        return False

    except smtplib.SMTPServerDisconnected:
        print("SMTP server disconnected.")
        return False

    except Exception as error:
        print("Failed to send mail: ", error)
        return False
        