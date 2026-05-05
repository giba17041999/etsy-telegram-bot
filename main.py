import os
import time
import requests
from imap_tools import MailBox, AND
from playwright.sync_api import sync_playwright

# 1. Lấy thông tin từ Biến môi trường (Thiết lập trên Railway Variables)
EMAIL = os.environ.get("EMAIL_ACCOUNT")
PASSWORD = os.environ.get("EMAIL_PASSWORD") 
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
IMAP_SERVER = "imap.gmail.com" 

def send_photo_to_telegram(photo_path, caption):
    """Hàm gửi ảnh qua Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        payload = {"chat_id": CHAT_ID, "caption": caption}
        files = {"photo": photo}
        response = requests.post(url, data=payload, files=files)
        return response.json()

def capture_email_html(html_content, output_file="email_screenshot.png"):
    """Hàm dựng HTML thành giao diện web và chụp ảnh"""
    temp_html_path = os.path.abspath("temp_email.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    file_url = f"file://{temp_html_path}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Thiết lập kích thước màn hình phù hợp để chụp email
        page = browser.new_page(viewport={"width": 600, "height": 800})
        page.goto(file_url)
        # Đợi một chút để render hoàn toàn
        time.sleep(2)
        page.screenshot(path=output_file, full_page=True)
        browser.close()
    
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

def check_mail():
    print("Đang quét email mới...")
    try:
        with MailBox(IMAP_SERVER).login(EMAIL, PASSWORD, 'INBOX') as mailbox:
            # Tìm các email chưa đọc
            for msg in mailbox.fetch(AND(seen=False)):
                print(f"-> Phát hiện email: {msg.subject}")
                
                # Lấy nội dung HTML hoặc Text
                html_content = msg.html or msg.text
                
                if html_content:
                    capture_email_html(html_content)
                    caption = f"📧 New Email: {msg.subject}\n👤 From: {msg.from_}"
                    send_photo_to_telegram("email_screenshot.png", caption)
                    print("Đã gửi ảnh chụp qua Telegram!")
                
                # Đánh dấu email là đã đọc để không gửi lại
                mailbox.seen(msg.uid, True)
                    
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    if not all([EMAIL, PASSWORD, BOT_TOKEN, CHAT_ID]):
        print("LỖI: Bạn chưa cài đặt đầy đủ Variables trên Railway!")
    else:
        print("Hệ thống bắt đầu chạy 24/7...")
        while True:
            check_mail()
            time.sleep(60) # Kiểm tra mỗi phút một lần
