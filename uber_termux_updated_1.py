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
        
        print(f"\n[+] Checking phone number: {phone_number}")
        driver.get(url)
        
        # Enter phone number
        wait = WebDriverWait(driver, 20)
        input_field = wait.until(EC.presence_of_element_located((By.ID, "PHONE_NUMBER_or_EMAIL_ADDRESS")))
        input_field.send_keys(phone_number)
        
        # Click continue button
        forward_button = driver.find_element(By.ID, "forward-button")
        forward_button.click()
        
        # Wait for result to appear
        time.sleep(10)
        
        page_source = driver.page_source
        
        banned_keywords = [
            "The phone number you entered is blocked",
            "Unable to create account",
            "Choose another option to continue"
        ]
        
        is_banned = any(keyword in page_source for keyword in banned_keywords)
        
        if is_banned:
            print(f"[-] Result for {phone_number}: Banned 🚫")
        else:
            if "Puzzle" in page_source or "Solve" in page_source:
                print(f"[!] Result for {phone_number}: Website requires puzzle/captcha solving ⚠️")
            else:
                print(f"[+] Result for {phone_number}: Account available or requires additional step ✅")
                
    except Exception as e:
        print(f"[!] Error occurred while checking {phone_number}: {e}")
    finally:
        if driver:
            driver.quit()

def main():
    print("--- Uber Phone Checker ---")
    print("1. Enter a single phone number")
    print("2. Enter path to file containing phone numbers")
    
    choice = input("\nChoose (1 or 2): ").strip()
    
    if choice == '1':
        phone = input("Enter phone number: ").strip()
        if phone:
            check_uber_phone(phone)
        else:
            print("Error: No phone number entered.")
            
    elif choice == '2':
        file_path = input("Enter file path: ").strip()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    numbers = [line.strip() for line in f if line.strip()]
                
                print(f"Found {len(numbers)} phone numbers. Starting check...")
                for num in numbers:
                    check_uber_phone(num)
                    time.sleep(2) # Small delay between each check
            except Exception as e:
                print(f"Error reading file: {e}")
        else:
            print(f"Error: Path '{file_path}' does not exist.")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
