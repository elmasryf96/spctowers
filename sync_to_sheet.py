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

# 2. تحديد مسار الاعتمادات (يعمل محلياً أو من مسار Secret Files في Render)
cred_path = "credentials.json"
if not os.path.exists(cred_path):
    cred_path = "/etc/secrets/credentials.json"

creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)

# 3. فتح الشيت المطلوب
sheet = client.open("SmartCollection_Cache").sheet1


def fetch_and_update():
    print("🔄 جاري سحب وتحديث البيانات من Smart Collection...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- حط كود تسجيل الدخول وسحب البيانات المعتاد هنا ---

        rows = [
            ["Tower Name", "Status", "Updated At"],
            ["Tower A", "Active", time.strftime("%Y-%m-%d %H:%M:%S")],
        ]

        sheet.clear()
        sheet.update(range_name="A1", values=rows)
        print("✅ تم تحديث Google Sheet بنجاح بالأبراج والعقود!")

        browser.close()


# 4. حلقة تكرار للعمل المستمر 24/7
while True:
    try:
        fetch_and_update()
    except Exception as e:
        print(f"❌ حدث خطأ أثناء السحب: {e}")

    print("⏳ الانتظار لمدة 60 ثانية قبل الفحص والتحديث التالي...")
    time.sleep(60)
