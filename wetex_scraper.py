#!/usr/bin/env python3
"""
WETEX Exhibitor Scraper using Selenium
Optimized for GitHub Codespaces
"""

import time
import json
import csv
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WETEXSeleniumScraper:
    """Selenium-based scraper for WETEX exhibitor data"""
    
    def __init__(self, headless=True):
        self.base_url = "https://www.wetex.ae/exhibit"
        self.headless = headless
        self.driver = None
        self.temp_dir = None
        
    def setup_driver(self):
        """Setup Chrome driver with options optimized for Codespaces"""
        import tempfile
        import os
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
        
        # Create a unique temporary directory for this session
        temp_dir = tempfile.mkdtemp(prefix='wetex_chrome_')
        
        # Essential options for Codespaces/Docker environments
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-data-dir={temp_dir}')  # Unique user data directory
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--remote-debugging-port=9222')  # Avoid port conflicts
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # Additional options to prevent conflicts
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-translate')
        
        # User agent to appear more like a regular browser
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Performance options
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Store temp directory for cleanup
        self.temp_dir = temp_dir
        
        # Initialize driver
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✓ Chrome driver initialized successfully")
        print(f"  Using temp directory: {temp_dir}")
        
    def wait_for_element(self, by, value, timeout=10):
        """Helper method to wait for elements"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"⚠ Timeout waiting for element: {value}")
            return None
    
    def debug_table_state(self):
        """Debug helper to check table state"""
        try:
            # Check if tbody exists
            tbody = self.driver.find_elements(By.ID, "tb_exhibit")
            print(f"  └─ tbody found: {len(tbody) > 0}")
            
            if tbody:
                # Check for rows
                rows = tbody[0].find_elements(By.TAG_NAME, "tr")
                print(f"  └─ Total tr elements: {len(rows)}")
                
                # Check for rows with specific class
                data_rows = tbody[0].find_elements(By.CLASS_NAME, "m19-table__content-table-row")
                print(f"  └─ Data rows with class: {len(data_rows)}")
                
                # Check first row content if exists
                if data_rows:
                    first_row_cells = data_rows[0].find_elements(By.TAG_NAME, "td")
                    print(f"  └─ First row cells: {len(first_row_cells)}")
                    if first_row_cells:
                        first_cell_text = first_row_cells[0].text[:50] if first_row_cells[0].text else "Empty"
                        print(f"  └─ First cell text: '{first_cell_text}...'")
                
                # Check innerHTML length
                inner_html = tbody[0].get_attribute("innerHTML")
                print(f"  └─ tbody innerHTML length: {len(inner_html)} chars")
                
        except Exception as e:
            print(f"  └─ Debug error: {str(e)}")
    
    def get_data_via_javascript(self, page_number: int = 0) -> List[Dict]:
        """Alternative method: Get data by executing the website's JavaScript directly"""
        exhibitors = []
        try:
            print("  └─ Attempting to fetch data via JavaScript...")
            
            # Execute the JavaScript function that the website uses
            script = f"""
            var pageNumber = {page_number};
            var records = 20;
            var orderBy = 1;
            var searchBy = 0;
            var type = 1;
            var search = '';
            
            // Make the AJAX call
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/umbraco/surface/wetexdatasurface/GetExhibitorList?PageNumber=' + pageNumber + 
                     '&Records=' + records + '&OrderBy=' + orderBy + '&SearchBy=' + searchBy + 
                     '&type=' + type + '&Search=' + search, false);
            xhr.send();
            
            if (xhr.status === 200) {{
                // Create a temporary div to parse the response
                var tempDiv = document.createElement('div');
                tempDiv.innerHTML = xhr.responseText;
                
                // Extract data from the response
                var rows = tempDiv.querySelectorAll('tr.m19-table__content-table-row');
                var data = [];
                
                rows.forEach(function(row) {{
                    var cells = row.querySelectorAll('td');
                    if (cells.length >= 7) {{
                        data.push({{
                            'name': cells[1].textContent.trim(),
                            'stand': cells[2].textContent.trim(),
                            'country': cells[3].textContent.trim(),
                            'sector': cells[4].textContent.trim(),
                            'activity': cells[5].textContent.trim(),
                            'hall': cells[6].textContent.trim()
                        }});
                    }}
                }});
                
                return data;
            }}
            return [];
            """
            
            result = self.driver.execute_script(script)
            
            if result:
                for item in result:
                    exhibitor_data = {
                        'Exhibitor Name': item.get('name', ''),
                        'Stand No': item.get('stand', ''),
                        'Country': item.get('country', ''),
                        'Sector': item.get('sector', ''),
                        'Business Activity': item.get('activity', ''),
                        'Hall': item.get('hall', '')
                    }
                    if exhibitor_data['Exhibitor Name']:
                        exhibitors.append(exhibitor_data)
                
                print(f"  └─ Successfully fetched {len(exhibitors)} exhibitors via JavaScript")
            
        except Exception as e:
            print(f"  └─ JavaScript fetch error: {str(e)}")
        
        return exhibitors
            
    def scrape_current_page(self) -> List[Dict]:
        """Scrape exhibitor data from the current page"""
        exhibitors = []
        
        try:
            # Wait for table to be present
            table = self.wait_for_element(By.CLASS_NAME, "m19-table__content-table")
            if not table:
                return exhibitors
            
            # Wait specifically for tbody to have data rows loaded
            WebDriverWait(self.driver, 15).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#tb_exhibit tr.m19-table__content-table-row")) > 0
            )
            
            # Additional wait to ensure data is fully rendered
            time.sleep(1)
            
            # Find all rows in tbody
            tbody = self.driver.find_element(By.ID, "tb_exhibit")
            rows = tbody.find_elements(By.CLASS_NAME, "m19-table__content-table-row")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.CLASS_NAME, "m19-table__content-table-cell")
                    
                    exhibitor_data = {
                        'Exhibitor Name': '',
                        'Stand No': '',
                        'Country': '',
                        'Sector': '',
                        'Business Activity': '',
                        'Hall': ''
                    }
                    
                    # Extract data from cells
                    cell_index = 0
                    for cell in cells:
                        cell_classes = cell.get_attribute('class') or ''
                        cell_text = cell.text.strip()
                        
                        if 'fixed-col' in cell_classes:
                            exhibitor_data['Exhibitor Name'] = cell_text
                        elif 'hidden-col' not in cell_classes:
                            if cell_index == 0:  # Stand No
                                exhibitor_data['Stand No'] = cell_text
                            elif cell_index == 1:  # Country
                                exhibitor_data['Country'] = cell_text
                            elif cell_index == 2:  # Sector
                                exhibitor_data['Sector'] = cell_text
                            elif cell_index == 3:  # Business Activity
                                exhibitor_data['Business Activity'] = cell_text
                            elif cell_index == 4:  # Hall
                                exhibitor_data['Hall'] = cell_text
                            cell_index += 1
                    
                    if exhibitor_data['Exhibitor Name']:
                        exhibitors.append(exhibitor_data)
                        
                except Exception as e:
                    print(f"⚠ Error processing row: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"⚠ Error scraping current page: {str(e)}")
            
        return exhibitors
    
    def click_page_number(self, page_num: int) -> bool:
        """Click on a specific page number"""
        try:
            # Method 1: Try clicking the page number directly
            page_xpath = f"//li[@data-num='{page_num}' and not(contains(@class, 'pagination-button'))]"
            page_elements = self.driver.find_elements(By.XPATH, page_xpath)
            
            if not page_elements:
                # Method 2: Try using JavaScript to trigger the pagination function
                print(f"  └─ Using JavaScript to navigate to page {page_num}")
                self.driver.execute_script(f"SetPageNumber({page_num})")
                time.sleep(3)  # Wait for AJAX to complete
                return True
            
            # Click the page element if found
            page_elem = page_elements[0]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", page_elem)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", page_elem)
            
            # Wait for new data to load
            time.sleep(3)
            
            # Wait for tbody to refresh with new data
            WebDriverWait(self.driver, 10).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#tb_exhibit tr.m19-table__content-table-row")) > 0
            )
            
            return True
            
        except Exception as e:
            print(f"  └─ Error clicking page {page_num}: {str(e)}")
            return False
    
    def scrape_all_pages(self, max_pages: int = None) -> List[Dict]:
        """Scrape all pages of exhibitor data"""
        all_exhibitors = []
        
        try:
            # Setup driver
            self.setup_driver()
            
            # Navigate to the page
            print(f"→ Navigating to {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for initial load - wait for the table AND data to be present
            print("⏳ Waiting for table data to load...")
            try:
                # Wait for the table structure
                self.wait_for_element(By.CLASS_NAME, "m19-table__content-table", timeout=15)
                
                # Wait for tbody to exist
                self.wait_for_element(By.ID, "tb_exhibit", timeout=10)
                
                # Additional wait for page to fully load
                time.sleep(5)
                
                print("✓ Page loaded successfully")
                
            except TimeoutException:
                print("⚠ Timeout waiting for table to load")
                print("  Attempting to continue anyway...")
            
            # Get total records and calculate pages
            try:
                # Sometimes the TotalRecords might not be loaded immediately
                total_elem = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "TotalRecords"))
                )
                
                # Wait for the element to have text
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(By.ID, "TotalRecords").text.strip() != ""
                )
                
                total_records = int(total_elem.text) if total_elem.text else 0
                records_per_page = 20
                total_pages = (total_records + records_per_page - 1) // records_per_page
                
                print(f"📊 Total records: {total_records}")
                print(f"📄 Total pages: {total_pages}")
                
                if max_pages:
                    total_pages = min(total_pages, max_pages)
                    print(f"🔸 Limiting to {max_pages} pages")
                    
            except Exception as e:
                print(f"⚠ Could not determine total pages: {str(e)}")
                # Try to get from pagination
                try:
                    pagination_items = self.driver.find_elements(By.CSS_SELECTOR, "#pagination li[data-num]")
                    page_numbers = [int(item.get_attribute("data-num")) for item in pagination_items if item.get_attribute("data-num").isdigit()]
                    total_pages = max(page_numbers) if page_numbers else 5
                    print(f"📄 Estimated pages from pagination: {total_pages}")
                except:
                    total_pages = max_pages or 5  # Default fallback
            
            # Scrape each page
            current_page = 1
            consecutive_failures = 0
            
            while current_page <= total_pages and consecutive_failures < 3:
                print(f"\n→ Scraping page {current_page}/{total_pages}")
                
                # Navigate to page if not the first
                if current_page > 1:
                    if not self.click_page_number(current_page):
                        # Try alternative navigation method
                        print(f"  └─ Trying alternative navigation for page {current_page}")
                        try:
                            # Call the JavaScript function directly (page numbers are 0-indexed in the function)
                            self.driver.execute_script(f"SetPageNumber({current_page - 1})")
                            time.sleep(3)
                        except:
                            consecutive_failures += 1
                            current_page += 1
                            continue
                
                # Debug table state
                print("  📋 Checking table state...")
                self.debug_table_state()
                
                # Wait for data to be present
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#tb_exhibit tr.m19-table__content-table-row")) > 0
                    )
                except TimeoutException:
                    print("  ⚠ Timeout waiting for data rows")
                
                # Scrape current page
                page_data = self.scrape_current_page()
                
                if page_data:
                    all_exhibitors.extend(page_data)
                    print(f"  ✓ Found {len(page_data)} exhibitors (Total: {len(all_exhibitors)})")
                    consecutive_failures = 0
                else:
                    print(f"  ⚠ No data found on page {current_page}")
                    
                    # Try scrolling to trigger lazy loading
                    print("  └─ Attempting to trigger data load by scrolling...")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(2)
                    
                    # Try again
                    page_data = self.scrape_current_page()
                    if page_data:
                        all_exhibitors.extend(page_data)
                        print(f"  ✓ Found {len(page_data)} exhibitors after scroll (Total: {len(all_exhibitors)})")
                        consecutive_failures = 0
                    else:
                        # Last resort: try JavaScript method
                        page_data = self.get_data_via_javascript(current_page - 1)  # 0-indexed
                        if page_data:
                            all_exhibitors.extend(page_data)
                            print(f"  ✓ Found {len(page_data)} exhibitors via JavaScript (Total: {len(all_exhibitors)})")
                            consecutive_failures = 0
                        else:
                            consecutive_failures += 1
                
                current_page += 1
                
                # Small delay between pages
                if current_page <= total_pages:
                    time.sleep(2)
            
            if consecutive_failures >= 3:
                print("\n⚠ Stopped due to consecutive failures")
                
        except Exception as e:
            print(f"\n❌ Fatal error during scraping: {str(e)}")
            
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Browser closed")
            
            # Clean up temporary directory
            if hasattr(self, 'temp_dir') and self.temp_dir:
                import shutil
                try:
                    shutil.rmtree(self.temp_dir)
                    print(f"✓ Cleaned up temp directory: {self.temp_dir}")
                except:
                    pass
                
        return all_exhibitors
    
    def save_to_csv(self, exhibitors: List[Dict], filename: str = "wetex_exhibitors.csv"):
        """Save exhibitor data to CSV file"""
        if not exhibitors:
            print("⚠ No data to save")
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Exhibitor Name', 'Stand No', 'Country', 'Sector', 'Business Activity', 'Hall']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(exhibitors)
            print(f"✓ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving CSV: {str(e)}")
    
    def save_to_json(self, exhibitors: List[Dict], filename: str = "wetex_exhibitors.json"):
        """Save exhibitor data to JSON file"""
        if not exhibitors:
            print("⚠ No data to save")
            return
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(exhibitors, f, indent=2, ensure_ascii=False)
            print(f"✓ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving JSON: {str(e)}")
    
    def display_summary(self, exhibitors: List[Dict]):
        """Display a summary of scraped data"""
        if not exhibitors:
            print("\n⚠ No exhibitors found")
            return
            
        print(f"\n" + "="*60)
        print(f"📊 SCRAPING SUMMARY")
        print(f"="*60)
        print(f"Total exhibitors scraped: {len(exhibitors)}")
        
        # Country statistics
        countries = {}
        for ex in exhibitors:
            country = ex.get('Country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n📍 Top Countries:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {country}: {count} exhibitors")
        
        # Sample data
        print(f"\n📋 Sample Exhibitors (first 3):")
        for i, ex in enumerate(exhibitors[:3], 1):
            print(f"\n  {i}. {ex['Exhibitor Name']}")
            print(f"     Stand: {ex['Stand No']} | Hall: {ex['Hall']}")
            print(f"     Country: {ex['Country']}")
            print(f"     Sector: {ex['Sector']}")

def main():
    """Main execution function"""
    print("🚀 WETEX Exhibitor Scraper (Selenium Version)")
    print("="*60)
    
    # Create scraper instance
    scraper = WETEXSeleniumScraper(headless=True)  # Set to False to see browser
    
    # Scrape data (limit to 3 pages for testing, remove limit for full scrape)
    print("\n📡 Starting web scraping...")
    exhibitors = scraper.scrape_all_pages(max_pages=3)  # Remove max_pages for all data
    
    # Display summary
    scraper.display_summary(exhibitors)
    
    # Save data
    if exhibitors:
        print(f"\n💾 Saving data...")
        scraper.save_to_csv(exhibitors)
        scraper.save_to_json(exhibitors)
        print(f"\n✅ Scraping completed successfully!")
    else:
        print(f"\n❌ No data was scraped")

if __name__ == "__main__":
    main()