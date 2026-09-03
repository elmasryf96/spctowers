import json
import os
import re
import time
import threading
from flask import Flask, jsonify
import gspread
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright

app = Flask(__name__)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# تحديد مكان ملف الاعتمادات
cred_path = "credentials.json"
if not os.path.exists(cred_path) and os.path.exists("/etc/secrets/credentials.json"):
    cred_path = "/etc/secrets/credentials.json"

def get_gspread_client():
    """إنشاء عميل Google Sheets"""
    with open(cred_path, "r", encoding="utf-8") as f:
        creds_dict = json.load(f)
    
    if "private_key" in creds_dict:
        creds_dict["private_key"] = re.sub(r"\\+n", "\n", creds_dict["private_key"])
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def fetch_and_update():
    """جلب البيانات وتحديث الشيت"""
    try:
        print("🔄 جاري سحب وتحديث البيانات من Smart Collection...")
        
        client = get_gspread_client()
        sheet = client.open("SmartCollection_Cache").sheet1
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # --- كود سحب البيانات هنا ---
            rows = [
                ["Tower Name", "Status", "Updated At"],
                ["Tower A", "Active", time.strftime("%Y-%m-%d %H:%M:%S")],
            ]
            
            sheet.clear()
            sheet.update(range_name="A1", values=rows)
            print("✅ تم تحديث Google Sheet بنجاح!")
            
            browser.close()
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء التحديث: {e}")

def background_updater():
    """تشغيل التحديث في الخلفية كل 60 ثانية"""
    while True:
        fetch_and_update()
        print("⏳ الانتظار 60 ثانية قبل التحديث التالي...")
        time.sleep(60)

# Routes للـ Health Check
@app.route('/')
@app.route('/health')
def health_check():
    return jsonify({
        "status": "running",
        "service": "smart-collection-sync",
        "message": "Background updater is active"
    }), 200

@app.route('/status')
def status():
    """للتحقق من حالة الخدمة"""
    return jsonify({
        "status": "ok",
        "background_thread": "running"
    }), 200

if __name__ == '__main__':
    # تشغيل التحديث في خلفية منفصلة
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()
    print("✅ Background updater started successfully!")
    
    # تشغيل Flask server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
