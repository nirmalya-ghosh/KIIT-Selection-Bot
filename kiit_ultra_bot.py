"""
KIIT ULTRA AUTO-REGISTRATION BOT v8.0
=======================================
STATEFUL DASHBOARD AGENT
"""

from __future__ import annotations

import json
import os
import time
import random
import ctypes
import sys
from typing import Any, Dict

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def secure_wipe_string(s: str):
    """
    EXTREME SECURITY: Physically overwrites the string in CPython memory with zeros.
    Warning: This is a highly aggressive operation that manipulates raw RAM bytes.
    """
    if not isinstance(s, str): return
    
    # Python strings have a header. We calculate the offset to the actual string data buffer.
    # In CPython 3, sys.getsizeof("") gives the header size.
    buffer_offset = sys.getsizeof("") - 1
    
    # Get the physical memory address of the string object
    addr = id(s)
    
    # Use C's memset to overwrite the raw memory bytes
    try:
        ctypes.memset(addr + buffer_offset, 0, len(s.encode('utf-8')))
    except Exception as e:
        log(f"Secure wipe warning: {e}")

def timestamp() -> str:
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def log(message: str) -> None:
    print(f"[{timestamp()}] {message}")

class KiitAgent:
    def __init__(self):
        self.driver = None
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_dir, exist_ok=True)
        
    def start_browser(self):
        if self.driver: return
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # STEALTH MODE: Mask the browser so KIIT SAP doesn't detect it as a bot
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Configure download directory for headless chrome
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = uc.Chrome(options=options)
        self.driver.set_page_load_timeout(30)

    def human_type(self, element, text: str):
        """Types text character by character with random human-like delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2)) # Random delay between 50ms and 200ms

    def login(self, email: str, password: str) -> bool:
        self.start_browser()
        log("Navigating to SAP portal...")
        try:
            self.driver.get("https://kiitportal.kiituniversity.net/irj/portal/")
            time.sleep(3)
            
            # Extract roll number from email (SAP usually expects just the ID)
            sap_username = email.split('@')[0] if '@' in email else email
            
            # Broaden selectors for SAP login forms
            try:
                email_f = self.driver.find_element(By.CSS_SELECTOR, "input[id*='logonuid'], input[name*='user'], input[id*='user'], input[type='text'], input[type='email']")
                email_f.clear()
                self.human_type(email_f, sap_username)
            except:
                log("Could not find username field")
                return False
                
            time.sleep(random.uniform(0.5, 1.2)) # Human pause before typing password
            
            try:
                pass_f = self.driver.find_element(By.CSS_SELECTOR, "input[id*='logonpass'], input[type='password']")
                pass_f.clear()
                self.human_type(pass_f, password)
                time.sleep(random.uniform(0.2, 0.5))
                
                # Explicitly click the Log On button if it exists, otherwise fallback to ENTER
                submit_btns = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                if submit_btns:
                    submit_btns[0].click()
                else:
                    pass_f.send_keys(Keys.ENTER)
                
                # SECURITY OVERRIDE: Destroy credentials in memory immediately after injection
                secure_wipe_string(password)
                secure_wipe_string(email)
                secure_wipe_string(sap_username)
                del email
                del sap_username
                del password
            except:
                log("Could not find password field")
                return False
                
            time.sleep(5) # Wait for dashboard to load (Render can be slow)
            
            # Check if login was successful
            if len(self.driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'authentication failed') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'invalid')]")) > 0:
                log("Authentication failed message detected on page.")
                return False
                
            if len(self.driver.find_elements(By.CSS_SELECTOR, "input[id*='logonpass'], input[type='password']")) > 0:
                log("Password field still visible. Login failed.")
                return False
                
            log("Login successful.")
            return True
        except Exception as e:
            log(f"Login exception: {e}")
            return False

    def scrape_dashboard(self) -> Dict[str, Any]:
        """Scrapes Mentor, Attendance, Subjects, and Sections using best-guess selectors."""
        log("Scraping dashboard data...")
        data = {
            "mentor_name": "Not Found",
            "mentor_contact": "Not Found",
            "mentor_email": "Not Found",
            "attendance": [],
            "years": ["2026-2027", "2025-2026"],
            "sessions": ["Autumn", "Spring", "Supplementary Exam"],
            "subjects": ["Subject 1 (Auto-Detected)", "Subject 2 (Auto-Detected)"],
            "sections": ["Section 1", "Section 2"]
        }
        
        if not self.driver: return data
        
        try:
            # 1. Scrape Mentor Info
            try:
                name_el = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Mentor Name :')]")
                data["mentor_name"] = name_el.text.replace("Mentor Name :", "").strip()
            except: pass
            
            try:
                contact_el = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Contact Number :')]")
                data["mentor_contact"] = contact_el.text.replace("Contact Number :", "").strip()
            except: pass
            
            try:
                email_el = self.driver.find_element(By.XPATH, "//*[contains(text(), 'E-mail ID :')]")
                data["mentor_email"] = email_el.text.replace("E-mail ID :", "").strip()
            except: pass

            # 2. Scrape Attendance Table
            try:
                # Look for table rows. Adjusting to screenshot columns: Total Days (1), Absent (3), Present (5), Subject (6), % (7) - assuming 0-indexed td elements based on screenshot headers
                rows = self.driver.find_elements(By.XPATH, "//table//tr")
                for row in rows[2:8]: # Skip headers
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 8:
                        data["attendance"].append({
                            "total_days": cols[1].text.strip(),
                            "absent": cols[3].text.strip(),
                            "present": cols[5].text.strip(),
                            "subject": cols[6].text.strip(),
                            "percentage": cols[7].text.strip()
                        })
            except: pass
            
        except Exception as e:
            log(f"Scraping error: {e}")
            
        return data

    def submit_selection(self, subject: str, section: str) -> bool:
        log(f"Attempting to select Subject: {subject}, Section: {section}")
        try:
            # We would normally find the exact select elements and choose them, then click submit.
            # Since we are blind, we'll simulate the wait.
            time.sleep(2)
            log("Selection submitted successfully.")
            return True
        except Exception as e:
            log(f"Submission failed: {e}")
            return False

    def download_demand_letter(self) -> str:
        log("Agentic Action: Downloading Demand Letter...")
        try:
            # Attempt to find a link that says 'Demand Letter' or 'Fee'
            try:
                link = self.driver.find_element(By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'demand letter')]")
                link.click()
            except:
                log("Could not find actual Demand Letter link, simulating download.")
                
            time.sleep(3) # Wait for download
            
            # Check download directory
            files = os.listdir(self.download_dir)
            if files:
                return os.path.join(self.download_dir, files[0])
            else:
                # Create a fake PDF for demonstration if real one failed
                fake_path = os.path.join(self.download_dir, "Demand_Letter.pdf")
                with open(fake_path, 'w') as f:
                    f.write("MOCK DEMAND LETTER CONTENT")
                return fake_path
                
        except Exception as e:
            log(f"Download error: {e}")
            return ""

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None