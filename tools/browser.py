import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
import time
import random

driver = None

def get_driver():
    global driver
    if driver is None:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") # CRITICAL for Docker memory limits
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Detect if we are running inside the Docker container
        if os.environ.get("RUNNING_IN_DOCKER") == "true":
            print("🐳 Docker detected: Running Chrome in Headless Mode...")
            options.add_argument("--headless=new")
            options.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Running locally on your Mac
            driver = webdriver.Chrome(options=options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
    return driver

def random_sleep(min_sec=1.5, max_sec=4.0):
    time.sleep(random.uniform(min_sec, max_sec))
