import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

# 1. إعداد الربط مع Google Sheets عن طريق ملف الاعتمادات
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# فتح الشيت المخصص
sheet = client.open("SmartCollection_Cache").sheet1

def sync_data():
    print("🔄 جاري سحب وتحديث البيانات من Smart Collection...")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # تسجيل الدخول
        page.goto("https://billing.smartcollection.co/Account/Login?ReturnUrl=/AdminPortal/Dashboard/Staff")
        page.get_by_role("textbox", name="Username/Email").fill("faris.e@smartcollection.co")
        page.get_by_role("textbox", name="Password").fill("fPGLks")
        page.get_by_role("button", name="Sign In").click()
        page.wait_for_load_state("networkidle")

        # الانتقال لصفحة العقود
        page.goto("https://billing.smartcollection.co/AdminPortal/Customers")
        page.wait_for_load_state("networkidle")

        # 1. سحب جميع الأبراج الموجودة
        options = page.locator("#Search_Property option").all()
        properties_dict = {}
        for opt in options:
            name = opt.inner_text().strip()
            val = opt.get_attribute("value")
            if val and name and name != "--- Select Property ---":
                properties_dict[name] = val

        # عناوين الأعمدة في Google Sheet
        rows = [["Property Name", "Property ID", "Contract No"]]

        # 2. المرور على كل برج وسحب العقود المربوطة بيه
        for prop_name, prop_id in properties_dict.items():
            page.locator("#Search_Property").select_option(str(prop_id))
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)

            page.get_by_role("textbox", name="--- Select ---").click()
            contracts_elements = page.locator("li.select2-results__option").all()
            
            for c in contracts_elements:
                c_text = c.inner_text().strip()
                if c_text and "Select" not in c_text:
                    rows.append([prop_name, str(prop_id), c_text])

        context.close()
        browser.close()

        # 3. كتابة البيانات المحدثة في Google Sheet
        sheet.clear()
        sheet.update("A1", rows)
        print("✅ تم تحديث Google Sheet بنجاح بالأبراج والعقود!")

# تشغيل عملية التحديث في حلقة تكرارية كل دقيقة
if __name__ == "__main__":
    while True:
        try:
            sync_data()
        except Exception as e:
            print(f"❌ حدث خطأ أثناء التحديث: {e}")
        
        print("⏳ الانتظار لمدة 60 ثانية قبل الفحص والتحديث التالي...")
        time.sleep(60)