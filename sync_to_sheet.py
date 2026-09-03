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

if "GOOGLE_CREDENTIALS" in os.environ:
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
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
        # تشغيل المتصفح في الوضع الخفي (Headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- أضف خطوات تسجيل الدخول وسحب البيانات الخاصة بك هنا ---
        # مثال لتأكيد عمل السكريبت وتحديث الشيت
        rows = [
            ["Tower Name", "Status", "Updated At"],
            ["Tower A", "Active", time.strftime("%Y-%m-%d %H:%M:%S")],
        ]

        # تحديث البيانات في الشيت
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
