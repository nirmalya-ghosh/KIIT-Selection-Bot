"""
KIIT ULTRA AUTO-REGISTRATION BOT v5.0
=======================================
FULLY AUTOMATED | SEMESTER + SECTION SELECTION

This bot automatically:
1. Logs into KIIT SAP Portal
2. Navigates to Section Selection
3. Clicks "3rd Semester" button
4. Selects the user's desired section from dropdown
5. Auto-clicks ADD and SUBMIT
6. Handles all edge cases

WARNING: Use at your own risk. This violates KIIT ToS.
"""

from __future__ import annotations

import getpass
import sys
import time
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any

from colorama import Fore, Style, init
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ==================== CONFIGURATION ====================
APP_NAME = "KIIT ULTRA BOT v5.0"
POLL_FREQUENCY = 0.01  # 10ms polling
MAX_WAIT = 15
MAX_RETRIES = 5

# ==================== UTILITY FUNCTIONS ====================

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def log(message: str, color: str = Fore.CYAN, prefix: str = "▸") -> None:
    print(f"{color}[{timestamp()}] [{prefix}] {message}{Style.RESET_ALL}")

def log_success(message: str) -> None:
    log(message, Fore.GREEN, "✓")

def log_error(message: str) -> None:
    log(message, Fore.RED, "✗")

def log_warning(message: str) -> None:
    log(message, Fore.YELLOW, "⚠")

def log_info(message: str) -> None:
    log(message, Fore.CYAN, "ℹ")

def log_performance(message: str) -> None:
    log(message, Fore.MAGENTA, "⚡")

def print_banner() -> None:
    print(Fore.RED + "=" * 70)
    print(f"  {APP_NAME}")
    print("  [FULL AUTO-REGISTRATION | NO HUMAN INTERVENTION]")
    print("=" * 70 + Style.RESET_ALL)
    print(Fore.RED + """
    ⚠️  CRITICAL WARNING ⚠️
    
    This bot AUTOMATICALLY registers you for courses.
    It WILL click ADD and SUBMIT buttons programmatically.
    
    Using this bot VIOLATES KIIT's Terms of Service.
    YOU ARE SOLELY RESPONSIBLE for any consequences.
    Press Ctrl+C NOW to abort, or press Enter to continue.
    """ + Style.RESET_ALL)
    input()

# ==================== INPUT COLLECTION ====================

def get_runtime_inputs() -> tuple[str, str, str, str, str, bool]:
    """Collect all user inputs at runtime."""
    print(Fore.CYAN + "\n[INPUT REQUIRED]" + Style.RESET_ALL)
    
    base_url = input("  [?] SAP Portal Base URL (e.g., https://sap.kiit.ac.in): ").strip()
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    
    email = input("  [?] KIIT Email: ").strip()
    password = getpass.getpass("  [?] SAP Password: ")
    
    print(Fore.YELLOW + "\n  Available Sections:" + Style.RESET_ALL)
    print("  CSE-01, CSE-02, CSE-03, CSE-04, CSE-05, CSE-06, CSE-07")
    print("  CSE-08, CSE-09, CSE-10, CSE-11, CSE-12, CSE-13, CSE-14")
    
    section = input("  [?] Desired Section (e.g., CSE-01): ").strip().upper()
    
    semester = input("  [?] Semester (3rd or 5th): ").strip()
    if semester not in ['3rd', '5th']:
        semester = '3rd'
        log_info(f"Defaulting to {semester} Semester")
    
    headless = input("  [?] Run in headless mode? (faster) [y/N]: ").strip().lower() == 'y'
    
    return base_url, email, password, section, semester, headless

# ==================== BROWSER SETUP ====================

def build_driver(headless: bool = False) -> WebDriver:
    """Create a high-performance Chrome driver."""
    options = Options()
    
    options.page_load_strategy = 'eager'
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--window-size=1920,1080')
    
    if headless:
        options.add_argument('--headless=new')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Stealth mode
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(0.5)
    
    return driver

# ==================== LOGIN ENGINE ====================

def find_element_fast(driver: WebDriver, selectors: list[str], timeout: float = 3) -> Any | None:
    """Ultra-fast element finder with multiple selector fallback."""
    start = time.perf_counter()
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                if elem.is_displayed() and elem.is_enabled():
                    return elem
        except:
            continue
        
        if time.perf_counter() - start > timeout:
            break
    
    return None

def perform_login(driver: WebDriver, email: str, password: str) -> bool:
    """Execute login with ultra-fast form filling."""
    log_info("Attempting login...")
    
    username_field = find_element_fast(driver, [
        "input[type='email']",
        "input[name*='user' i]",
        "input[id*='user' i]",
        "input[name*='email' i]",
        "input[type='text']"
    ])
    
    if not username_field:
        log_error("Username field not found")
        return False
    
    password_field = find_element_fast(driver, [
        "input[type='password']",
        "input[name*='pass' i]",
        "input[id*='pass' i]"
    ])
    
    if not password_field:
        log_error("Password field not found")
        return False
    
    driver.execute_script("arguments[0].value = arguments[1];", username_field, email)
    driver.execute_script("arguments[0].value = arguments[1];", password_field, password)
    
    submit_button = find_element_fast(driver, [
        "button[type='submit']",
        "input[type='submit']",
        "button[id*='login' i]",
        "button[name*='login' i]",
        "input[value*='Log' i]"
    ])
    
    if submit_button:
        driver.execute_script("arguments[0].click();", submit_button)
    else:
        password_field.send_keys(Keys.ENTER)
    
    log_success("Login credentials submitted")
    return True

def login_with_retry(driver: WebDriver, base_url: str, email: str, password: str) -> None:
    """Handle login with retry on failure."""
    max_attempts = 3
    
    for attempt in range(max_attempts):
        log_info(f"Navigating to portal (attempt {attempt + 1}/{max_attempts})...")
        driver.get(base_url)
        time.sleep(0.5)
        
        if "password" not in driver.page_source.lower():
            log_success("Already logged in")
            return
        
        if perform_login(driver, email, password):
            time.sleep(1.5)
            if "password" not in driver.page_source.lower():
                log_success("Login successful!")
                return
            else:
                log_warning("Login may have failed, retrying...")
                continue
        else:
            log_error(f"Login attempt {attempt + 1} failed")
    
    raise RuntimeError("Failed to login after multiple attempts")

# ==================== NAVIGATION TO SECTION SELECTION ====================

def navigate_to_section_selection(driver: WebDriver) -> bool:
    """Navigate to the Section Selection page."""
    log_info("Navigating to Section Selection...")
    
    try:
        # Look for "Section Selection" link
        section_selectors = [
            "a:contains('Section Selection')",
            "a[href*='section' i]",
            "a[href*='Section' i]",
            "a[href*='register' i]",
            "a[href*='booking' i]",
            "span:contains('Section Selection')",
            "div:contains('Section Selection')"
        ]
        
        # Try JavaScript to find by text
        script = """
        const links = document.querySelectorAll('a, span, div');
        for (let el of links) {
            if (el.textContent && el.textContent.trim() === 'Section Selection') {
                return el;
            }
        }
        return null;
        """
        section_element = driver.execute_script(script)
        
        if section_element:
            driver.execute_script("arguments[0].click();", section_element)
            log_success("Clicked Section Selection")
            time.sleep(1)
            return True
        
        # Try finding by partial link text
        try:
            element = driver.find_element(By.PARTIAL_LINK_TEXT, "Section")
            driver.execute_script("arguments[0].click();", element)
            log_success("Found Section link")
            time.sleep(1)
            return True
        except:
            pass
        
        # Try direct navigation if URL is known
        log_warning("Could not find Section Selection link, trying direct navigation...")
        current_url = driver.current_url
        if 'sap' in current_url:
            # Try common patterns
            test_urls = [
                current_url + "/section",
                current_url.replace("home", "section"),
                current_url.replace("portal", "registration")
            ]
            for url in test_urls:
                try:
                    driver.get(url)
                    time.sleep(0.5)
                    return True
                except:
                    continue
        
        return False
        
    except Exception as e:
        log_error(f"Navigation error: {str(e)}")
        return False

# ==================== SEMESTER SELECTION ====================

def select_semester(driver: WebDriver, semester: str) -> bool:
    """Click the semester button (3rd or 5th)."""
    log_info(f"Selecting {semester} Semester...")
    
    try:
        # Look for semester buttons
        script = f"""
        const elements = document.querySelectorAll('button, a, div, span');
        for (let el of elements) {{
            const text = el.textContent || '';
            if (text.trim() === '{semester} Semester' || text.includes('{semester}')) {{
                return el;
            }}
        }}
        return null;
        """
        semester_element = driver.execute_script(script)
        
        if semester_element:
            driver.execute_script("arguments[0].click();", semester_element)
            log_success(f"Selected {semester} Semester")
            time.sleep(0.5)
            return True
        
        # Try finding by text
        try:
            element = driver.find_element(By.XPATH, f"//*[contains(text(), '{semester}')]")
            driver.execute_script("arguments[0].click();", element)
            log_success(f"Selected {semester} Semester")
            time.sleep(0.5)
            return True
        except:
            pass
        
        log_error(f"Could not find {semester} Semester button")
        return False
        
    except Exception as e:
        log_error(f"Semester selection error: {str(e)}")
        return False

# ==================== SECTION SELECTION ====================

def select_section(driver: WebDriver, section: str) -> bool:
    """Select the desired section from dropdown/list."""
    log_info(f"Selecting section {section}...")
    
    try:
        # First, try to find and click the dropdown/select element
        dropdown_selectors = [
            "select",
            "select[id*='section' i]",
            "select[name*='section' i]",
            "select[class*='section' i]",
            "div[class*='dropdown'] select",
            "div[class*='select'] select"
        ]
        
        dropdown = find_element_fast(driver, dropdown_selectors, timeout=2)
        
        if dropdown:
            # Use JavaScript to select the option
            script = f"""
            const select = arguments[0];
            const options = select.options;
            for (let i = 0; i < options.length; i++) {{
                if (options[i].text.includes('{section}') || options[i].value.includes('{section}')) {{
                    select.selectedIndex = i;
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
            }}
            return false;
            """
            result = driver.execute_script(script, dropdown)
            if result:
                log_success(f"Selected {section} from dropdown")
                time.sleep(0.3)
                return True
        
        # Try clicking on the section directly (if it's a button/link)
        script = f"""
        const elements = document.querySelectorAll('button, a, div, span, li, td');
        for (let el of elements) {{
            const text = el.textContent || '';
            if (text.includes('{section}') || text.includes('{section.replace('CSE-', '')}')) {{
                const parent = el.closest('tr') || el.parentElement;
                if (parent) {{
                    const clickables = parent.querySelectorAll('button, a, input[type="button"], input[type="submit"]');
                    for (let clickable of clickables) {{
                        if (clickable.textContent.includes('Select') || clickable.textContent.includes('Add')) {{
                            return clickable;
                        }}
                    }}
                    return el;
                }}
                return el;
            }}
        }}
        return null;
        """
        section_element = driver.execute_script(script)
        
        if section_element:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section_element)
            time.sleep(0.05)
            driver.execute_script("arguments[0].click();", section_element)
            log_success(f"Clicked on {section}")
            time.sleep(0.3)
            return True
        
        log_error(f"Could not find section {section}")
        return False
        
    except Exception as e:
        log_error(f"Section selection error: {str(e)}")
        return False

# ==================== SUBMIT REGISTRATION ====================

def submit_registration(driver: WebDriver) -> bool:
    """Click the Submit button to finalize registration."""
    log_info("Submitting registration...")
    
    try:
        # Find Submit button
        submit_selectors = [
            "button:contains('Submit')",
            "input[type='submit'][value*='Submit' i]",
            "button[type='submit']:contains('Submit')",
            "button[id*='submit' i]",
            "input[value='Submit']",
            "button:contains('SUBMIT')"
        ]
        
        # Try JavaScript to find Submit button
        script = """
        const elements = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
        for (let el of elements) {
            const text = (el.textContent || el.value || '').toLowerCase();
            if (text.includes('submit') || text.includes('confirm') || text.includes('finish')) {
                return el;
            }
        }
        return null;
        """
        submit_button = driver.execute_script(script)
        
        if submit_button:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
            time.sleep(0.05)
            driver.execute_script("arguments[0].click();", submit_button)
            log_success("Clicked Submit button")
            time.sleep(0.5)
            return True
        
        log_error("Could not find Submit button")
        return False
        
    except Exception as e:
        log_error(f"Submit error: {str(e)}")
        return False

# ==================== VERIFICATION ====================

def verify_registration(driver: WebDriver) -> bool:
    """Check if registration was successful."""
    log_info("Verifying registration...")
    time.sleep(0.5)
    
    page_text = driver.page_source.lower()
    
    success_indicators = ['success', 'confirmed', 'registered', 'enrolled', 'thank you', 'submitted']
    for indicator in success_indicators:
        if indicator in page_text:
            log_success(f"Registration confirmed! (found '{indicator}')")
            return True
    
    error_indicators = ['error', 'failed', 'invalid', 'not available', 'full', 'dues']
    for indicator in error_indicators:
        if indicator in page_text:
            log_error(f"Registration may have failed (found '{indicator}')")
            return False
    
    log_warning("Could not determine registration status")
    return False

# ==================== MAIN REGISTRATION ENGINE ====================

def auto_register(driver: WebDriver, section: str, semester: str) -> bool:
    """
    Complete automated registration flow:
    1. Navigate to Section Selection
    2. Select Semester
    3. Select Section
    4. Submit Registration
    """
    log_info("🚀 STARTING AUTO-REGISTRATION... 🚀")
    start_time = time.perf_counter()
    
    # Step 1: Navigate to Section Selection
    if not navigate_to_section_selection(driver):
        log_error("Failed to navigate to Section Selection")
        return False
    
    time.sleep(0.5)
    
    # Step 2: Select Semester
    if not select_semester(driver, semester):
        log_error(f"Failed to select {semester} Semester")
        return False
    
    time.sleep(0.3)
    
    # Step 3: Select Section
    if not select_section(driver, section):
        log_error(f"Failed to select section {section}")
        return False
    
    time.sleep(0.3)
    
    # Step 4: Submit Registration
    if not submit_registration(driver):
        log_error("Failed to submit registration")
        return False
    
    # Step 5: Verify
    success = verify_registration(driver)
    
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    log_performance(f"Registration completed in {elapsed_ms:.1f} ms")
    
    return success

# ==================== MAIN EXECUTION ====================

def run_bot() -> None:
    """Main bot execution flow."""
    init(autoreset=True)
    print_banner()
    
    base_url, email, password, section, semester, headless = get_runtime_inputs()
    
    driver: WebDriver | None = None
    start_time = time.perf_counter()
    
    try:
        log_info("Initializing Chrome driver...")
        driver = build_driver(headless)
        
        # Login
        login_with_retry(driver, base_url, email, password)
        
        # AUTOMATIC REGISTRATION
        success = auto_register(driver, section, semester)
        
        # Report results
        total_time = time.perf_counter() - start_time
        
        print(Fore.CYAN + "\n" + "=" * 70)
        if success:
            print(Fore.GREEN + f"✅ REGISTRATION COMPLETED SUCCESSFULLY for {section}")
        else:
            print(Fore.RED + f"❌ REGISTRATION FAILED for {section}")
        print(Fore.CYAN + f"⏱️  Total execution time: {total_time:.2f} seconds")
        print("=" * 70 + Style.RESET_ALL)
        
        if not headless:
            input("\n[?] Press Enter to close the browser...")
    
    except KeyboardInterrupt:
        log_warning("Bot interrupted by user")
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
                log_info("Browser closed")
            except:
                pass

def main() -> None:
    try:
        run_bot()
    except Exception as e:
        print(Fore.RED + f"[FATAL] {str(e)}" + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()