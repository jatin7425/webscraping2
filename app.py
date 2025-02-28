import json
import concurrent
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup ChromeDriver
service = Service("ChromeDriver/chromedriver")  # Ensure this path is correct
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in background
driver = webdriver.Chrome(service=service, options=options)

def find_categories():
    """Extracts product categories from Dell's support page."""
    try:
        driver.get("https://www.dell.com/support/home/en-in")

        # Click "Browse All Products" button
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn-homedashboard-browse-all-product"))
        ).click()
        print("✅ Clicked 'Browse All Products' button successfully!")

        # Wait for the pop-up to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dds__modal__body"))
        )
        print("✅ Pop-up loaded successfully!")

        # Wait for product category cards
        links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
        )

        # Extract category names and URLs
        return [
            {
                "category": link.find_element(By.TAG_NAME, "h6").get_attribute("innerHTML").strip(),
                "URL": link.find_element(By.TAG_NAME, "a").get_attribute("href")
            }
            for link in links
        ]

    except Exception as e:
        print("❌ Error:", e)
        return []
    
found_categories = find_categories()

def process_categories(param, data_path_value=""):
    """Processes categories and extracts subcategories based on data-path."""
    processed_categories = []
    
    for category in param:
        driver.get(category['URL'])
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dds__modal__body"))
        )
        print(f"✅ Pop-up loaded successfully! {category['category']}")

        try:
            links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, f"//a[@data-path='{data_path_value}']"))
            )
        except Exception as e:
            print(f"❌ Error fetching subcategories for {category['category']}: {e}")
            continue
        
        for link in links:
            print(f"🔍 Found subcategory: {category['category']} → {link.text.strip()}")
            values = {
                "parent_category": category['category'],
                "category": link.text.strip(),
                "URL": link.get_attribute("href")
            }
            processed_categories.append(values)
    
    return processed_categories

# Run the functions
first_level_categories = process_categories(found_categories)
second_level_categories = []
for item in first_level_categories:
    second_level_categories.append(process_categories([item], item['category']))
    
def get_itrate_net_subCategory(param):
    """Processes categories and extracts subcategories based on data-path."""
    processed_categories = []
    
    for category in param:
        driver.get(category['URL'])
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dds__modal__body"))
        )
        print(f"✅ Pop-up loaded successfully! {category['category']}")
        
        data_path_value = f"{category['parent_category']}@,{category['category']}"
        try:
            links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, f"//a[@data-path='{data_path_value}']"))
            )
        except Exception as e:
            print(f"❌ Error fetching subcategories for {category['category']}: {e}")
            print(f" returning : \n(parent_category: {category['parent_category']},\n category: {category['category']},\n URL: {category['URL']} )")
            Naviagate_to_productpage(category)
            return category
        
        for link in links:
            print(f"🔍 Found deeper subcategory: {category['category']} → {link.text.strip()}")
            print(f"data : \n(parent_category: {category['category']},\n category: {link.text.strip()},\n URL: {link.get_attribute('href')} )")
            values = {
                "parent_category": category['category'],
                "category": link.text.strip(),
                "URL": link.get_attribute("href")
            }
            processed_categories.append(values)

    # Recursively process subcategories and flatten results
    subcategories = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_itrate_net_subCategory, [item]): item for item in processed_categories}
        for future in concurrent.futures.as_completed(futures):
            subcategories.extend(future.result())
    return subcategories

def Naviagate_to_productpage(category):
    """Navigates to the product page and interacts with products."""
    driver.get(category['URL'])
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dds__modal__body"))
        )
        print(f"✅ Pop-up loaded successfully! {category['category']}")

        while True:
            try:
                products = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "product-list-item"))
                )
                break  # Exit loop if elements are successfully found
            except:
                print("🔄 Retrying to locate product elements due to stale reference...")

        for index in range(len(products)):
            try:
                # Re-fetch product list to avoid stale reference
                products = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "product-list-item"))
                )

                # Ensure index is within bounds
                if index >= len(products):
                    print("❌ Skipping: Product index out of range")
                    continue
                
                product = products[index]

                # Scroll into view and click using JavaScript (avoids some stale issues)
                driver.execute_script("arguments[0].scrollIntoView();", product)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "product-list-item"))
                )
                driver.execute_script("arguments[0].click();", product)
                print("✅ Clicked on product successfully!")

                # Get current URL after navigation
                current_url = driver.current_url
                print(f"🔗 Navigated to: {current_url}")

                # Call function to fetch product details
                fetch_product_dets(current_url)

                # Navigate back to product listing page before clicking the next product
                driver.get(category['URL'])

            except Exception as e:
                print(f"❌ Could not click product: {e}")

    except Exception as e:
        print(f"❌ Error navigating to product page: {e}")


def fetch_product_dets(url):
    try:
        driver.get("https://www.dell.com/support/home/en-in")
        print("hello")
    except:
        print("error")


for items in second_level_categories:
    for item in items:
        get_itrate_net_subCategory([item])

# Close the browser after everything is done
driver.quit()
