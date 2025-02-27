from selenium import webdriver
from selenium.webdriver.chrome.service import Service

try:
    service = Service("ChromeDriver/chromedriver")  # Correct path for Linux
    print(f"Using ChromeDriver at {service.path}")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without opening a browser

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.google.com")
    print("Chrome WebDriver is working!")
    driver.quit()
except Exception as e:
    print("Error:", e)
