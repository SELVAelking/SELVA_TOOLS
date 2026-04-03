import requests
import uuid
import sys
import json
import os
import time

# --- إعدادات الألوان ---
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# --- إعدادات الملفات والبيانات ---
KEYS_FILE = "api_keys.json"
ADMIN_PASS = "1929"
DEFAULT_EMAIL = "mohaymen012@gmail.com"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        # مفتاح افتراضي للبدء
        initial_keys = ["SELVA-2024", "selva"]
        with open(KEYS_FILE, 'w') as f:
            json.dump(initial_keys, f)
        return initial_keys
    with open(KEYS_FILE, 'r') as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f)

# --- وظيفة طباعة المقدمة ---
def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    banner = f"""
{Colors.BOLD}{Colors.CYAN}
  ██████  ███████ ██      ██    ██  █████      ██████      ████████  ██████   ██████  ██      
 ██       ██      ██      ██    ██ ██   ██    ██    ██        ██    ██    ██ ██    ██ ██      
  █████   █████   ██      ██    ██ ███████    ██    ██        ██    ██    ██ ██    ██ ██      
      ██  ██      ██       ██  ██  ██   ██    ██    ██        ██    ██    ██ ██    ██ ██      
 ██████   ███████ ███████   ████   ██   ██     ██████         ██     ██████   ██████  ███████ 
{Colors.END}
{Colors.BOLD}{Colors.MAGENTA}========================================================================================={Colors.END}
{Colors.BOLD}{Colors.YELLOW}                            SELVA & TOOL - OTP AUTOMATION{Colors.END}
{Colors.BOLD}{Colors.MAGENTA}========================================================================================={Colors.END}
"""
    print(banner)

# --- وظائف Bolt الأساسية ---
def bolt_login(phone_number):
    url = "https://node.taxify.eu/driver-auth/partnerDriverWeb/startAuthentication/"
    device_id = str(uuid.uuid4())
    params = {"version": "DP.12.77", "brand": "bolt", "deviceId": device_id, "device_name": "Linux", "language": "en", "device_os_version": "x86_64"}
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = {"phone": phone_number}
    try:
        response = requests.post(url, params=params, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0 or "message" not in result:
                print(f"{Colors.GREEN}{Colors.BOLD}DONE LOGIN ✅ ({phone_number}){Colors.END}")
                return True
            else: print(f"{Colors.RED}{Colors.BOLD}FAILED LOGIN ❌ ({phone_number}): {result.get('message')}{Colors.END}")
        else: print(f"{Colors.RED}{Colors.BOLD}FAILED LOGIN ❌ ({phone_number}): Status {response.status_code}{Colors.END}")
    except Exception as e: print(f"{Colors.RED}{Colors.BOLD}ERROR LOGIN ❌ ({phone_number}): {e}{Colors.END}")
    return False

def bolt_registration(phone_number, email=DEFAULT_EMAIL):
    url = "https://driverregistration.live.boltsvc.net/driverRegistration/startRegistration"
    params = {"version": "HP.1.22.7", "device_name": "HP", "device_os_version": "web", "deviceId": "web", "deviceType": "web", "language": "ar-ae"}
    payload = {"email": email, "phone": phone_number, "city_id": 643, "terms_consent_accepted": 1}
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        response = requests.post(url, params=params, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print(f"{Colors.GREEN}{Colors.BOLD}DONE registration ✅ ({phone_number}){Colors.END}")
                return True
            else: print(f"{Colors.RED}{Colors.BOLD}FAILED registration ❌ ({phone_number}): {result.get('message')}{Colors.END}")
        else: print(f"{Colors.RED}{Colors.BOLD}FAILED registration ❌ ({phone_number}): Status {response.status_code}{Colors.END}")
    except Exception as e: print(f"{Colors.RED}{Colors.BOLD}ERROR registration ❌ ({phone_number}): {e}{Colors.END}")
    return False

def process_file(file_path, action_func):
    if not os.path.exists(file_path):
        print(f"{Colors.RED}{Colors.BOLD}Error: File '{file_path}' not found.{Colors.END}")
        return
    with open(file_path, 'r') as f:
        numbers = [line.strip() for line in f if line.strip()]
    print(f"{Colors.CYAN}Processing {len(numbers)} numbers from file...{Colors.END}")
    for num in numbers:
        if not num.startswith('+'): num = '+' + num
        action_func(num)
        time.sleep(1)

# --- نظام الإدارة (Admin) ---
def admin_panel():
    password = input(f"{Colors.YELLOW}Enter Admin Password: {Colors.END}")
    if password != ADMIN_PASS:
        print(f"{Colors.RED}Wrong Password! Access Denied.{Colors.END}")
        return

    while True:
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}--- ADMIN PANEL ---{Colors.END}")
        print(f"{Colors.BLUE}1. Add New API Key{Colors.END}")
        print(f"{Colors.BLUE}2. List All Keys{Colors.END}")
        print(f"{Colors.BLUE}3. Delete API Key{Colors.END}")
        print(f"{Colors.BLUE}4. Exit Admin{Colors.END}")
        
        adm_choice = input(f"\n{Colors.YELLOW}Select Option: {Colors.END}").strip()
        keys = load_keys()

        if adm_choice == '1':
            new_key = input(f"{Colors.YELLOW}Enter New API Key Name: {Colors.END}").strip()
            if new_key and new_key not in keys:
                keys.append(new_key)
                save_keys(keys)
                print(f"{Colors.GREEN}Key '{new_key}' added successfully!{Colors.END}")
            else: print(f"{Colors.RED}Invalid or Duplicate Key.{Colors.END}")
        
        elif adm_choice == '2':
            print(f"\n{Colors.CYAN}Current Keys:{Colors.END}")
            for i, k in enumerate(keys, 1): print(f"{i}. {k}")
        
        elif adm_choice == '3':
            del_key = input(f"{Colors.YELLOW}Enter Key to Delete: {Colors.END}").strip()
            if del_key in keys:
                keys.remove(del_key)
                save_keys(keys)
                print(f"{Colors.GREEN}Key '{del_key}' deleted.{Colors.END}")
            else: print(f"{Colors.RED}Key not found.{Colors.END}")
            
        elif adm_choice == '4': break
        else: print(f"{Colors.RED}Invalid Choice.{Colors.END}")

# --- الواجهة الرئيسية ---
def main():
    print_banner()
    
    # التحقق من API Key في البداية
    keys = load_keys()
    user_key = input(f"{Colors.YELLOW}{Colors.BOLD}Please Enter Your API KEY to Start: {Colors.END}").strip()
    
    if user_key not in keys:
        print(f"{Colors.RED}{Colors.BOLD}INVALID API KEY! Please contact the owner.{Colors.END}")
        sys.exit()
    
    print(f"{Colors.GREEN}Access Granted! Welcome.{Colors.END}")
    time.sleep(1)

    while True:
        print_banner()
        print(f"{Colors.BLUE}{Colors.BOLD}1_ SIGN IN (Login){Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}2_ SIGN UP (Registration){Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}3_ MIX (Login & Registration){Colors.END}")
        print(f"{Colors.MAGENTA}{Colors.BOLD}4_ ADMIN (Settings){Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}0_ EXIT{Colors.END}")
        
        choice = input(f"\n{Colors.YELLOW}Select Option: {Colors.END}").strip()
        
        if choice == '0': break
        elif choice == '4': admin_panel()
        elif choice in ['1', '2', '3']:
            print(f"\n{Colors.CYAN}{Colors.BOLD}1_ ONE NUMBER{Colors.END}")
            print(f"{Colors.CYAN}{Colors.BOLD}2_ FILE NUMBER{Colors.END}")
            sub_choice = input(f"{Colors.YELLOW}Select Option (1 or 2): {Colors.END}").strip()
            
            if sub_choice == '1':
                phone = input(f"{Colors.YELLOW}Enter phone number (with +): {Colors.END}").strip()
                if not phone.startswith('+'): phone = '+' + phone
                if choice == '1': bolt_login(phone)
                elif choice == '2': bolt_registration(phone)
                elif choice == '3':
                    bolt_login(phone)
                    bolt_registration(phone)
                    
            elif sub_choice == '2':
                path = input(f"{Colors.YELLOW}Enter file path: {Colors.END}").strip()
                if choice == '1': process_file(path, bolt_login)
                elif choice == '2': process_file(path, bolt_registration)
                elif choice == '3':
                    def mix_func(num):
                        bolt_login(num)
                        bolt_registration(num)
                    process_file(path, mix_func)
            else: print(f"{Colors.RED}Invalid selection.{Colors.END}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
        else: print(f"{Colors.RED}Invalid selection.{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Exiting...{Colors.END}")
        sys.exit(0)
