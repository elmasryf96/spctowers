import base64
import json
import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

# 1. إعداد صلاحيات Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# قراءة الاعتمادات وفك تشفير Base64 من بيئة Render أو من الملف المحلي
if "GOOGLE_CREDENTIALS" in os.environ:
    raw_b64 = os.environ["GOOGLE_CREDENTIALS"]
    decoded_json = base64.b64decode(raw_b64).decode("utf-8")
    creds_json = json.loads(decoded_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

client = gspread.authorize(creds)

# 2. فتح الشيت المطلوب
sheet = client.open("SmartCollection_Cache").sheet1


def fetch_and_update():
    print("🔄 جاري سحب وتحديث البيانات من Smart Collection...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- حط كود تسجيل الدخول وسحب البيانات المعتاد هنا ---

        # مثال لتحديث البيانات في الشيت:
        rows = [
            ["Tower Name", "Status", "Updated At"],
            ["Tower A", "Active", time.strftime("%Y-%m-%d %H:%M:%S")],
        ]

        sheet.clear()
        sheet.update(range_name="A1", values=rows)
        print("✅ تم تحديث Google Sheet بنجاح بالأبراج والعقود!")

        browser.close()


# 3. حلقة تكرار للعمل المستمر 24/7
while True:
    try:
        fetch_and_update()
    except Exception as e:
        print(f"❌ حدث خطأ أثناء السحب: {e}")

    print("⏳ الانتظار لمدة 60 ثانية قبل الفحص والتحديث التالي...")
    time.sleep(60)
