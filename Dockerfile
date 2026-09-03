FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# نسخ الملفات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت متصفحات Playwright
RUN playwright install

COPY . .

# تشغيل التطبيق
CMD ["python", "sync_to_sheet.py"]
