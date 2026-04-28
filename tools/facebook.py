import os
import time
import random
import pickle
import getpass
from langchain_core.tools import tool
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tools.browser import get_driver, random_sleep

COOKIES_FILE = "facebook_cookies.pkl"

@tool
def login_to_facebook() -> str:
    """Login to Facebook and save session cookies."""
    try:
        driver = get_driver()
        driver.get("https://www.facebook.com")
        random_sleep(2, 4)

        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            random_sleep(3, 5)
            return "✅ Logged in using saved cookies!"

        print("\n🔐 First-time Facebook login:")
        email = input("Facebook Email/Phone: ")
        password = getpass.getpass("Facebook Password: ")

        wait = WebDriverWait(driver, 15)
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(email)
        random_sleep(1, 2)

        pass_field = driver.find_element(By.ID, "pass")
        pass_field.send_keys(password)
        pass_field.send_keys(Keys.RETURN)

        random_sleep(6, 9)

        with open(COOKIES_FILE, "wb") as f:
            pickle.dump(driver.get_cookies(), f)

        return "✅ Login successful! Cookies saved for future use."

    except Exception as e:
        return f"❌ Login error: {str(e)}"

@tool
def post_to_facebook(message: str) -> str:
    """Post a message on your Facebook profile."""
    try:
        driver = get_driver()
        if "facebook.com" not in driver.current_url:
            driver.get("https://www.facebook.com/me")
            random_sleep(4, 6)

        wait = WebDriverWait(driver, 12)
        post_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Create a post']")))
        post_box.click()
        random_sleep(1.5, 3)

        active = driver.switch_to.active_element
        for char in message:
            active.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        random_sleep(1, 2)
        post_btn = driver.find_element(By.XPATH, "//div[@aria-label='Post']")
        post_btn.click()
        random_sleep(4, 7)

        return f"✅ Successfully posted to Facebook!"

    except Exception as e:
        return f"❌ Facebook posting error: {str(e)}"

@tool
def go_to_facebook_profile() -> str:
    """Open your Facebook profile."""
    try:
        driver = get_driver()
        driver.get("https://www.facebook.com/me")
        random_sleep(3, 5)
        return "✅ Opened your Facebook profile."
    except Exception as e:
        return f"❌ Error: {str(e)}"
