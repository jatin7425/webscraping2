import random
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
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)

def fetch_categories():
    """Extract category names and their identifiers."""
    soup = BeautifulSoup(response.text, "html.parser")

    categories = soup.find_all("a", class_="linked-card")

    if not categories:
        print("No categories found. Check 'output.html' for debugging.")
        return {}

    category_map = {}
    for category in categories:
        title = category.find("h6").get_text(strip=True) if category.find("h6") else "N/A"
        identifier = category.get("data-path", "N/A")
        if identifier != "N/A":
            category_map[title] = identifier

    return category_map

def get_first_level_category(categories):
    """Fetch product details for each category."""
    for category_name, category_id in categories.items():
        product_url = f"{PRODUCTS_FIRST_CATEGORY_API}?category={category_id}&country=in&language=en&region=ap&segment=bsd&customerset=inbsd1&appName=home&version=v2&inccomponents=False&isolated=False"

        response = requests.get(product_url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sub_categories = soup.find_all("a", data-path="")
            
            for category in sub_categories:
                pass
            
            print(f"Fetched products for: {category_name} ({category_id})")
        else:
            print(f"Failed to fetch products for {category_name} (Status: {response.status_code})")

if response.status_code == 200:
    categories = fetch_categories()
    get_first_level_category(categories)
else:
    print("Failed to fetch the page. Try checking the URL or headers.")
