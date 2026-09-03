FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تشغيل سيرفر بسيط في الخلفية للرد على Render + تشغيل السكريبت
CMD python -m http.server $PORT & python sync_to_sheet.py
