# Sử dụng bản build sẵn của Playwright cho Python
FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app

# Copy danh sách thư viện
COPY requirements.txt .

# Cài đặt thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt Chromium và các dependencies hệ thống
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy mã nguồn
COPY . .

# Chạy ứng dụng
CMD ["python", "main.py"]
