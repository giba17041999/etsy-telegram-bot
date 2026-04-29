import imaplib
import email
import requests
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("haanhtuanetsy@gmail.com")
PASSWORD = os.getenv("lgjuymixrdsvkmvp")

BOT_TOKEN = os.getenv("8687189308:AAG0IKJPF84WnsXB6DxGKvcltu81222njzY")
CHAT_ID = os.getenv("7242802148")


def send_to_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    requests.post(url, data=data)


def check_email():

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)

    mail.select("inbox")

    status, messages = mail.search(None, 'UNSEEN')

    email_ids = messages[0].split()

    for e_id in email_ids:

        status, msg_data = mail.fetch(e_id, "(RFC822)")

        for response_part in msg_data:

            if isinstance(response_part, tuple):

                msg = email.message_from_bytes(response_part[1])

                subject = msg["subject"]
                sender = msg["from"]

                body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()

                else:
                    body = msg.get_payload(decode=True).decode()

                message = f"""
📦 NEW ORDER EMAIL

From: {sender}

Subject: {subject}

Details:
{body[:800]}
"""

                send_to_telegram(message)


if __name__ == "__main__":

    check_email()
