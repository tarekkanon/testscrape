from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Setup Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

try:
    # Navigate to page
    print("Loading page...")
    driver.get("https://www.wetex.ae/exhibit")
    
    # Wait for page to load
    time.sleep(10)
    
    # Check what's in the tbody
    print("\n1. Checking tbody existence:")
    tbody = driver.find_elements(By.ID, "tb_exhibit")
    print(f"   tbody found: {len(tbody) > 0}")
    
    if tbody:
        # Check innerHTML
        inner_html = tbody[0].get_attribute("innerHTML")
        print(f"   innerHTML length: {len(inner_html)} chars")
        print(f"   First 500 chars: {inner_html[:500]}")
        
        # Check for rows
        rows = tbody[0].find_elements(By.TAG_NAME, "tr")
        print(f"\n2. Found {len(rows)} tr elements")
        
        # Check first row
        if rows:
            cells = rows[0].find_elements(By.TAG_NAME, "td")
            print(f"   First row has {len(cells)} cells")
            if cells:
                print(f"   First cell text: '{cells[0].text}'")
    
    # Try executing JavaScript to get data
    print("\n3. Trying JavaScript to fetch data:")
    result = driver.execute_script("""
        var tbody = document.getElementById('tb_exhibit');
        if (tbody) {
            var rows = tbody.getElementsByTagName('tr');
            return {
                'tbody_exists': true,
                'row_count': rows.length,
                'first_row_text': rows.length > 0 ? rows[0].innerText : 'No rows'
            };
        }
        return {'tbody_exists': false};
    """)
    print(f"   Result: {result}")
    
finally:
    driver.quit()