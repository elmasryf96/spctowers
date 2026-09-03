import json
import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# 1. تحديد مكان الملف (محلي أو من Render Secret Files)
cred_path = "credentials.json"
if not os.path.exists(cred_path) and os.path.exists(
    "/etc/secrets/credentials.json"
):
  cred_path = "/etc/secrets/credentials.json"

# 2. قراءة الملف وتصليح أسطر private_key المكسورة أوتوماتيكياً
with open(cred_path, "r", encoding="utf-8") as f:
  creds_dict = json.load(f)

if "private_key" in creds_dict:
  creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
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
