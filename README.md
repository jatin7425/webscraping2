# 🖥️ Dell Support Product Scraper

This script scrapes product categories and subcategories from Dell's support page using Python and BeautifulSoup. It navigates through various product levels and extracts product details.

## ✨ Features
- 🏷️ Scrapes Dell's support product categories
- 🔄 Iterates through subcategories to find final product pages
- 💾 Saves extracted data to `output.json`
- 🏗️ Handles nested category structures recursively
- 🛡️ Uses random user-agents to prevent blocking

## 📦 Requirements
- 🐍 Python 3.x
- Required Python libraries:
  ```bash
  pip install requests beautifulsoup4
  ```

## ⚙️ How It Works
1. **📂 Fetch Main Categories**
   - Calls Dell's API to retrieve all product categories.
2. **🗂️ Iterate Through Categories**
   - Extracts `data-path` values and navigates deeper.
3. **🔍 Detects Product Pages**
   - If a category has no further subcategories, it fetches the product list.
4. **📄 Save Data**
   - Extracted product details are saved to `output.json`.

## 🚀 Usage
Run the script with:
```bash
python scraper.py
```

## 📊 Output
The script creates an `output.json` file containing:
```json
[
  {
    "itration_path": ["Laptops", "Alienware", "Alienware 13"],
    "data_info": { "productCode": "alienware-13" },
    "text": "Alienware 13"
  }
]
```

## 🌍 API Endpoints Used
- **🔗 Main Categories API:**
  ```
  https://www.dell.com/support/components/productselector/allproducts?country=in&language=en&region=ap&segment=bsd&customerset=inbsd1&appName=incidents&version=v2
  ```
- **📡 Category Products API:**
  ```
  https://www.dell.com/support/components/productselector/getproducts?category={category_id}&country=in&language=en
  ```

## ⚠️ Notes
- 🔄 Make sure to update the `Cookie` value in `headers` if requests are getting blocked.
- 🔀 Adjust `User-Agent` rotation if Dell applies additional bot-detection mechanisms.
- 🏗️ The script may require modifications if Dell changes its website structure.

## 📜 License
📝 MIT License

