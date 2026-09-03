import json
import os
import re
import time
import gspread
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# 1. تحديد مكان ملف الاعتمادات
cred_path = "credentials.json"
if not os.path.exists(cred_path) and os.path.exists(
    "/etc/secrets/credentials.json"
):
  cred_path = "/etc/secrets/credentials.json"


def get_gspread_client():
  # قراءة الملف ومعالجة المفتاح بـ Regex لحل أي أخطاء في الـ Newlines
  with open(cred_path, "r", encoding="utf-8") as f:
    creds_dict = json.load(f)

  if "private_key" in creds_dict:
    creds_dict["private_key"] = re.sub(
        r"\\+n", "\n", creds_dict["private_key"]
    )

  creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
  return gspread.authorize(creds)


def fetch_and_update():
  print("🔄 جاري سحب وتحديث البيانات من Smart Collection...")

  # فتح الشيت جوه الدالة لحماية السكريبت من السقوط أثناء مشاكل الشبكة
  client = get_gspread_client()
  sheet = client.open("SmartCollection_Cache").sheet1

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # --- حط كود سحب البيانات المعتاد هنا ---
    rows = [
        ["Tower Name", "Status", "Updated At"],
        ["Tower A", "Active", time.strftime("%Y-%m-%d %H:%M:%S")],
    ]

    sheet.clear()
    sheet.update(range_name="A1", values=rows)
    print("✅ تم تحديث Google Sheet بنجاح بالأبراج والعقود!")

    browser.close()


# 2. حلقة التكرار المستمرة 24/7
while True:
  try:
    fetch_and_update()
  except Exception as e:
    print(f"❌ حدث خطأ أثناء السحب: {e}")

  print("⏳ الانتظار لمدة 60 ثانية قبل الفحص والتحديث التالي...")
  time.sleep(60)
