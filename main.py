import imaplib
import email
import os
import time
import requests

EMAIL = os.getenv("haanhtuanetsy@gmail.com")
PASSWORD = os.getenv("lgjuymixrdsvkmvp")
BOT_TOKEN = os.getenv("8687189308:AAG0IKJPF84WnsXB6DxGKvcltu81222njzY")
CHAT_ID = os.getenv("7242802148")

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

def check_orders():
    print("Checking Etsy orders...")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)

    mail.select("inbox")

    status, messages = mail.search(None, '(UNSEEN FROM "etsy.com")')

    if status != "OK":
        return

    for num in messages[0].split():
        status, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg["subject"]

        send_telegram(f"New Etsy Order:\n{subject}")

while True:
    try:
        check_orders()
    except Exception as e:
        print("Error:", e)

    time.sleep(60)
