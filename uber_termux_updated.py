import sys
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_uber_phone(phone_number):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        url = "https://auth.uber.com/v2?marketing_vistor_id=9c12110f-8d9a-40a4-913a-e41949bb50fd&next_url=https%3A%2F%2Fwww.uber.com&uclick_id=9b56bb71-a568-41ea-a5b3-5aede4ac2584"
        
        print(f"\n[+] جاري فحص الرقم: {phone_number}")
        driver.get(url)
        
        # إدخال رقم الهاتف
        wait = WebDriverWait(driver, 20)
        input_field = wait.until(EC.presence_of_element_located((By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS")))
        input_field.send_keys(phone_number)
        
        # الضغط على زر المتابعة
        forward_button = driver.find_element(By.ID, "forward-button")
        forward_button.click()
        
        # الانتظار لظهور النتيجة
        time.sleep(10)
        
        page_source = driver.page_source
        
        banned_keywords = [
            "The phone number you entered is blocked",
            "رقم الهاتف الذي أدخلته محظور",
            "Unable to create account",
            "يتعذر إنشاء الحساب",
            "Choose another option to continue"
        ]
        
        is_banned = any(keyword in page_source for keyword in banned_keywords)
        
        if is_banned:
            print(f"[-] النتيجة لـ {phone_number}: Banned 🚫")
        else:
            if "Puzzle" in page_source or "Solve" in page_source:
                print(f"[!] النتيجة لـ {phone_number}: الموقع يطلب حل لغز (Puzzle/Captcha) ⚠️")
            else:
                print(f"[+] النتيجة لـ {phone_number}: الحساب متاح أو يتطلب خطوة إضافية ✅")
                
    except Exception as e:
        print(f"[!] حدث خطأ أثناء فحص {phone_number}: {e}")
    finally:
        if driver:
            driver.quit()

def main():
    print("--- Uber Phone Checker ---")
    print("1. إدخال رقم هاتف واحد")
    print("2. إدخال مسار ملف يحتوي على أرقام")
    
    choice = input("\nاختر (1 أو 2): ").strip()
    
    if choice == '1':
        phone = input("أدخل رقم الهاتف: ").strip()
        if phone:
            check_uber_phone(phone)
        else:
            print("خطأ: لم يتم إدخال رقم.")
            
    elif choice == '2':
        file_path = input("أدخل مسار الملف: ").strip()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    numbers = [line.strip() for line in f if line.strip()]
                
                print(f"تم العثور على {len(numbers)} رقم. بدء الفحص...")
                for num in numbers:
                    check_uber_phone(num)
                    time.sleep(2) # تأخير بسيط بين كل فحص
            except Exception as e:
                print(f"خطأ في قراءة الملف: {e}")
        else:
            print(f"خطأ: المسار '{file_path}' غير موجود.")
    else:
        print("اختيار غير صحيح.")

if __name__ == "__main__":
    main()
