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

# قراءة الاعتمادات من بيئة Render أو من الملف المحلي
if "GOOGLE_CREDENTIALS" in os.environ:
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])

    # تصليح الـ private_key لو تم تشويه الـ newlines بواسطة Render
    if "private_key" in creds_json:
        creds_json["private_key"] = creds_json["private_key"].replace(
            "\\n", "\n"
        )

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
