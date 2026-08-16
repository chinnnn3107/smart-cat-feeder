import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST=os.getenv("SMTP_HOST")
SMTP_PORT=int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL=os.getenv("SMTP_EMAIL")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD")

alertSent = False

def sendEmail(to_email, subject, body):
    message = EmailMessage()

    message["From"] = SMTP_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(message)

        print("[Email] Email sent successfully.")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[Email] Email authentication failed.")
        return False

    except smtplib.SMTPServerDisconnected:
        print("[Email] SMTP server disconnected.")
        return False

    except Exception as error:
        print("[Email] Failed to send mail: ", error)
        return False

def checkHopperAlert(hopper_status, receiver_email):
    global alertSent

    if hopper_status <= 10 and alertSent == False:
        subject = "Smart Cat Feeder - Low Food Alert"
        
        body = f"""
The food level in the hopper is currently at {hopper_status}%.

Please refill the hopper to ensure your cat has enough food.

Smart Cat Feeder
        """
        if sendEmail(receiver_email, subject, body):
            alertSent = True

    elif hopper_status > 10:
        alertSent = False

        