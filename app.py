import json
import random
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.dell.com/support/components/productselector/"
PRODUCTS_FIRST_CATEGORY_API = "https://www.dell.com/support/components/productselector/getproducts"

url = f"{BASE_URL}allproducts?country=in&language=en&region=ap&segment=bsd&customerset=inbsd1&appName=incidents&version=v2"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_1data-vmpath5_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

headers = {
    "User-Agent": random.choice(user_agents),
    "Referer": "https://www.dell.com/support/home/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "application/json, text/plain, */*",
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "bm_sv=YOUR_UPDATED_COOKIE_HERE"
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)

def fetch_categories():
    """Extract category names and their identifiers."""
    soup = BeautifulSoup(response.text, "html.parser")

    categories = soup.find_all("a", attrs={"data-path": True})  
    print(f"Found {len(categories)} categories.")

    if not categories:
        print("No categories found. Check 'output.html' for debugging.")
        return {}

    category_map = []
    for category in categories:
        title = category.find("h6")
        if title:
            title_text = title.get_text(strip=True)
            category_id = category.get("data-path")  
            if category_id:
                category_map.append({
                    "category_name" : title_text,
                    "category_id" : category_id
                })
                print(f"Category found: {title_text} -> {category_id}")

    return category_map


def get_first_level_category(categories):
    """Fetch product details for each category."""
    
    sub_category_map = []
    for category in categories:
        
        category_name = category['category_name']
        category_id = category['category_id']
        
        if re.search(r'(_&|_and|&|and)', category_id, flags=re.IGNORECASE):
            # Remove unwanted words if found
            cleaned_text = re.sub(r'_and_|_&|_and|&|and', '_', category_id)
            cleaned_text = re.sub(r'_+', '_', cleaned_text)  # Remove any duplicate underscores
        else:
            cleaned_text = category_id
            
        product_url = f"{PRODUCTS_FIRST_CATEGORY_API}?category={cleaned_text}&country=in&language=en&region=ap&segment=bsd&customerset=inbsd1&appName=home&version=v2&inccomponents=False&isolated=False"

        response = requests.get(product_url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            sub_categories = soup.find_all("a", attrs={"data-ghost": category_name, "data-path": ""})
            
            if not sub_categories:
                print(f"No subcategories found for {category_name}.")
                continue
            
            for category in sub_categories:
                data_vmpath = category.get("data-vmpath", "N/A")  # Extract 'data-vmpath' attribute
                inner_text = category.get_text(strip=True)  # Extract the inner text

                if data_vmpath and inner_text:
                    sub_category_map.append({
                        "itration_path": [category_name , inner_text],
                        "current_category": inner_text,
                        "data-vmpath": data_vmpath
                    })
                    print(f"2nd Subcategory found: {category_name} -> {inner_text}")
            
        else:
            print(f"Failed to fetch products for {category_name} (Status: {response.status_code})")
    
    return sub_category_map


def iterate_to_depth(category):
    """Recursively fetch subcategories"""
    sub_category_map = []
    
    itration_path = category["itration_path"]
    current_category = category["current_category"]
    data_vmpath = category["data-vmpath"]
    
    # Build proper data-path for subcategories
    if 'previous_category' in category:
        previous_category = category['previous_category']
        data_path = f"{previous_category}@,{current_category}"
    else:
        data_path = current_category

    product_url = f"{PRODUCTS_FIRST_CATEGORY_API}?category={data_vmpath}&country=in&language=en&region=ap&segment=bsd&customerset=inbsd1&appName=incidents&version=v2"

    response = requests.get(product_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")    

        print(f"Fetching subcategories for {data_path} in {current_category}")

        sub_categories = soup.find_all("a", attrs={"data-path": data_path})  

        if not sub_categories:
            # print(f"No subcategories found for {current_category}.")
            fetch_product_list(category)
            return [category]

        for sub in sub_categories:
            data_vmpath = sub.get("data-vmpath")
            this_category = sub.get_text(strip=True)
            if this_category:
                sub_category_map.append({
                    "itration_path": itration_path + [this_category],
                    "previous_category": current_category,
                    "current_category": this_category,
                    "data-vmpath": data_vmpath
                })
                print(f"Subcategory found: {current_category} -> {this_category}")

        # Recursively fetch deeper subcategories
        all_subcategories = [category]  # Include current category in results
        for sub_category in sub_category_map:
            all_subcategories.extend(iterate_to_depth(sub_category))

        return all_subcategories

    else:
        print(f"Failed to fetch products for {current_category} (Status: {response.status_code})")
        return [category]


def fetch_product_list(category):
    """fetching product list"""
    itration_path = category["itration_path"]
    current_category = category["current_category"]
    data_vmpath = category["data-vmpath"]
    
    product_url = f"{PRODUCTS_FIRST_CATEGORY_API}?category={data_vmpath}&country=in&language=en&region=ap&segment=bsd&customerset=inbsd1&appName=incidents&version=v2&_=1740802427092"
    
    response = requests.get(product_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")    
        print(f"Fetching Product for: {current_category}")
        
        products = soup.find_all("a", class_="product-list-item")
        
        products_dets = []
        
        for product in products:
            data_info = product.get("data-info")
            text = product.get_text(strip=True)
            prod = {
                "itration_path": itration_path + [text],
                "data_info" : data_info,
                "text" : text
            }
            # navigate_to_support_page(prod)
            print({f"Updating ({prod['text']}) in output.json file."})
            if isinstance(prod['data_info'], str):
                try:
                    prod['data_info'] = json.loads(prod['data_info'])
                except json.JSONDecodeError:
                    print("Error decoding JSON in data_info")
                
                try:
                    with open("output.json", "r+", encoding="utf-8") as f:
                        existing_data = json.load(f)  # Load current JSON data
                        existing_data.extend(products_dets)  # Add new data
                        f.seek(0)  # Move pointer to the beginning of the file
                        json.dump(existing_data, f, indent=4, ensure_ascii=False)
                except (FileNotFoundError, json.JSONDecodeError):
                    # Create new file if it doesn't exist
                    with open("output.json", "w", encoding="utf-8") as f:
                        json.dump(products_dets, f, indent=4, ensure_ascii=False)
                
                
            products_dets.append(prod)

def navigate_to_support_page(product):
    data_info = product['data_info']
    
    if isinstance(data_info, str): 
        try:
            data_info = json.loads(data_info)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in navigate_to_support_page: {data_info}")
            data_info = {}
    
    product_code = data_info.get('productCode', 'N/A')
    
    url = f"https://www.dell.com/support/contactus/en-in/ContactUs/GetProductDashboard?serviceTag=&productCode={product_code}&agreementID=&isTrident=false&isEmcUser=false"

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(response.text)  # Get the full HTML response
        else:
            print(f"Failed to fetch page, status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error making request: {e}")

# Fetch categories only if the response is OK
if response.status_code == 200:
    categories = fetch_categories()
    if categories:
        first_level_categories = get_first_level_category(categories)
        for category in first_level_categories:
            iterate_to_depth(category)
else:
    print("Failed to fetch the page. Check the URL or headers.")
