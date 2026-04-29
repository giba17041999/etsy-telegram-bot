import imaplib
import email
import os
import time
import requests
from bs4 import BeautifulSoup

EMAIL = os.environ.get("haanhtuanetsy@gmail.com")
PASSWORD = os.environ.get("vsakjtetibpbjymn")
BOT_TOKEN = os.environ.get("8687189308:AAG0IKJPF84WnsXB6DxGKvcltu81222njzY")
CHAT_ID = os.environ.get("7242802148")


def send_message(text):

    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram variables missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print("Send message error:", e)


def send_photo(photo, caption):

    if not BOT_TOKEN or not CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    try:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "photo": photo,
                "caption": caption,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print("Send photo error:", e)


def get_html(msg):

    try:

        if msg.is_multipart():

            for part in msg.walk():

                if part.get_content_type() == "text/html":

                    html = part.get_payload(decode=True)

                    if html:
                        return html.decode(errors="ignore")

        else:

            if msg.get_content_type() == "text/html":

                html = msg.get_payload(decode=True)

                if html:
                    return html.decode(errors="ignore")

    except Exception as e:
        print("HTML parse error:", e)

    return ""


def parse_email(html):

    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n")

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    product = "Unknown"
    total = "Unknown"
    personalization = "None"
    shipping = "Unknown"
    image = None

    # find product
    try:

        for tag in soup.find_all(["h1", "h2", "h3"]):

            t = tag.get_text().strip()

            if len(t) > 5 and "etsy" not in t.lower():

                product = t
                break

    except:
        pass

    # find price
    try:

        for l in lines:

            if "$" in l and "." in l:

                total = l
                break

    except:
        pass

    # find personalization
    try:

        for l in lines:

            if "personalization" in l.lower():

                personalization = l
                break

    except:
        pass

    # find shipping address
    try:

        start = False
        addr = []

        for l in lines:

            low = l.lower()

            if "ship to" in low or "shipping address" in low:

                start = True
                continue

            if start:

                addr.append(l)

                if len(addr) >= 5:
                    break

        if addr:
            shipping = "\n".join(addr)

    except:
        pass

    # find product image
    try:

        for img in soup.find_all("img"):

            src = img.get("src")

            if not src:
                continue

            if "etsyimg.com" in src:

                image = src
                break

    except:
        pass

    return product, total, personalization, shipping, image


def check_orders():

    if not EMAIL or not PASSWORD:

        print("Email login missing")
        return

    try:

        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        mail.login(EMAIL, PASSWORD)

        mail.select("inbox")

        status, data = mail.search(None, '(UNSEEN SUBJECT "You made a sale")')

        ids = data[0].split()

        for num in ids:

            status, msg_data = mail.fetch(num, "(RFC822)")

            raw_email = msg_data[0][1]

            msg = email.message_from_bytes(raw_email)

            html = get_html(msg)

            if not html:
                continue

            product, total, personalization, shipping, image = parse_email(html)

            caption = f"""
🛒 <b>NEW ETSY ORDER</b>

📦 Product:
{product}

✏️ Personalization:
{personalization}

💰 Total:
{total}

🏠 Shipping address:
{shipping}
"""

            if image:

                send_photo(image, caption)

            else:

                send_message(caption)

        mail.logout()

    except Exception as e:

        print("Check order error:", e)


while True:

    try:

        print("Checking Etsy orders...")

        check_orders()

    except Exception as e:

        print("Loop error:", e)

    time.sleep(60)
