import json
import re
import concurrent
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

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
                "family": category['category'],
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
            # print(category)
            if "LOB" in category:
                Navigate_to_productPage(category)
            return category
        
        for link in links:
            print(f"🔍 Found deeper subcategory: {category['category']} → {link.text.strip()}")
            # print(category)
            values = {
                "family": category['family'],
                "LOB" : category.get("LOB", category["category"]),
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

def Navigate_to_productPage(category):
    """Navigates to the product page and interacts with products."""
    driver.get(category['URL'])
    try:
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dds__modal__body"))
        )
        if not modal:
            print("Pop-up not found")
        else:
            print(f"✅ Pop-up loaded successfully for Navigation! {category['category']}")

        while True:
            i = 0
            try:
                products = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "product-list-item"))
                )
                break  # ✅ Successfully found elements, exit loop
            except StaleElementReferenceException:
                print(f"🔄 Attempt {i + 1}: Retrying due to stale element reference...")
            except TimeoutException:
                print(f"❌ Attempt {i + 1}: Timed out while waiting for product elements...")
                break  # No point in retrying if timeout occurs
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                break

        for index in range(len(products)):
            try:
                # 🔄 Re-fetch elements on each iteration
                products = driver.find_elements(By.CLASS_NAME, "product-list-item")  
                if index >= len(products):  # Ensure index is within range
                    break  
                product = products[index]

                driver.execute_script("arguments[0].scrollIntoView();", product)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "product-list-item"))
                )
                product.click()

                # 🔄 Re-fetch button after page update
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "phProductUrl"))
                )
                navigate_Button = driver.find_element(By.ID, "phProductUrl")
                driver.execute_script("arguments[0].scrollIntoView();", navigate_Button)
                navigate_Button.click()

                current_url = driver.current_url
                fetch_product_dets(current_url, category)

            except StaleElementReferenceException:
                print(f"🔄 Stale Element, retrying product {index}...")
                continue
            except Exception as e:
                print(f"❌ Error clicking product {index}: {e}")
                continue
            
    except Exception as e:
        print(f"❌ Error navigating to product page: {e}")

def fetch_product_dets(url, category):
    
    def extract_product_code(url):
        """Extracts the product model from the given URL."""
        print(f"🔍 Debug: Checking URL - {url}")  # Debugging Line
        match = re.search(r'product/([^/]+)/overview', url)  # Corrected regex
        return match.group(1) if match else "Unknown Model"
    
    try:
        driver.get(url)
        category.update({"Product Code": extract_product_code(url)})
        # Append JSON object to a file

    except:
        print("error")


for items in second_level_categories:
    for item in items:
        get_itrate_net_subCategory([item])

# Close the browser after everything is done
driver.quit()
