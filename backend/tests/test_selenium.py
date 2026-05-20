# test_selenium.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

def test_login_and_redirect():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:

        driver.get("http://localhost:5173/login")
        
        login_input = wait.until(EC.presence_of_element_located((By.NAME, "login")))
        password_input = driver.find_element(By.NAME, "password")
        
        login_input.send_keys("testuser")
        password_input.send_keys("12345678")
        password_input.send_keys(Keys.RETURN)
        
        wait.until(EC.title_contains("BeatMarket"))
        assert "BeatMarket" in driver.title
        print("✅ Тест Selenium пройден: Авторизация и редирект работают.")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_and_redirect()