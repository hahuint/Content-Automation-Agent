from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open Facebook
driver.get("https://www.facebook.com")

print("✅ Chrome opened and Facebook loaded!")
time.sleep(5)  # Keep browser open for 5 seconds

driver.quit()
