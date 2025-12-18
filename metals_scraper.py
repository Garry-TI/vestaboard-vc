"""
Web scraper for Kitco precious metals prices.
Fetches Gold and Silver bid/ask prices from Kitco.com.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class MetalsScraper:
    """Scraper for Kitco precious metals prices."""

    def __init__(self):
        """Initialize the metals scraper."""
        self.gold_url = "https://www.kitco.com/charts/gold"
        self.silver_url = "https://www.kitco.com/charts/silver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.driver = None

    def fetch_prices(self) -> Dict[str, any]:
        """
        Fetch Gold and Silver prices from Kitco.

        Returns:
            Dictionary containing price data for Gold and Silver
        """
        try:
            print(f"[DEBUG] fetch_prices called - fetching fresh data from Kitco")
            # Fetch gold prices
            gold_data = self._fetch_metal_from_chart('gold', self.gold_url)

            # Fetch silver prices
            silver_data = self._fetch_metal_from_chart('silver', self.silver_url)

            # Validate that we got data
            if not gold_data or not silver_data:
                return {
                    'status': 'error',
                    'message': 'Failed to extract price data from Kitco',
                    'data': None
                }

            prices = {
                'gold': gold_data,
                'silver': silver_data
            }

            return {
                'status': 'success',
                'message': 'Prices fetched successfully',
                'data': prices
            }

        except requests.exceptions.ReadTimeout:
            return {
                'status': 'error',
                'message': 'kitco.com website down. Precious metals SPOT PRICES are NOT UP TO DATE.',
                'data': None,
                'timeout': True
            }
        except requests.RequestException as e:
            # Check if the error message contains "Read timed out"
            if "Read timed out" in str(e):
                return {
                    'status': 'error',
                    'message': 'kitco.com website down. Precious metals SPOT PRICES are NOT UP TO DATE.',
                    'data': None,
                    'timeout': True
                }
            return {
                'status': 'error',
                'message': f'Network error: {str(e)}',
                'data': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error fetching prices: {str(e)}',
                'data': None
            }

    def _init_driver(self):
        """Initialize the Selenium WebDriver if not already initialized."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')

            # Use webdriver-manager to handle ChromeDriver installation
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("[DEBUG] Selenium WebDriver initialized")

    def _fetch_metal_from_chart(self, metal_name: str, url: str) -> Optional[Dict]:
        """
        Fetch price data for a specific metal from its chart page using Selenium.

        Args:
            metal_name: Name of the metal (e.g., 'gold', 'silver')
            url: URL of the metal's chart page

        Returns:
            Dictionary with metal data or None if not found
        """
        try:
            # Initialize driver if needed
            self._init_driver()

            # Load the page
            print(f"[DEBUG] Loading {metal_name} page: {url}")
            self.driver.get(url)

            # Wait for the bid price element to be present and visible
            # This ensures JavaScript has loaded and updated the prices
            wait = WebDriverWait(self.driver, 20)
            bid_element = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//h3[contains(@class, 'text-4xl') and contains(@class, 'font-bold') and contains(@class, 'font-mulish')]"
                ))
            )

            # Wait a bit more for JavaScript to update the price
            time.sleep(2)

            # Get the page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find the bid price - it's in an h3 with specific classes
            bid_h3 = soup.find('h3', class_=lambda x: x and 'text-4xl' in x and 'font-bold' in x and 'font-mulish' in x)
            if not bid_h3:
                print(f"Could not find bid price for {metal_name}")
                return None

            bid_price = bid_h3.get_text(strip=True)
            print(f"[DEBUG] {metal_name} - Found bid price: {bid_price}")

            # Find the ask price - look for the "Ask" label and get the price next to it
            ask_price = None
            ask_divs = soup.find_all('div', class_=lambda x: x and 'text-sm' in str(x) and 'font-normal' in str(x))
            for ask_div in ask_divs:
                if 'Ask' in ask_div.get_text():
                    # The price is in the sibling div with text-[19px] and font-normal classes
                    parent = ask_div.parent
                    price_div = parent.find('div', class_=lambda x: x and 'text-[19px]' in str(x) and 'font-normal' in str(x))
                    if price_div:
                        ask_price = price_div.get_text(strip=True)
                        print(f"[DEBUG] {metal_name} - Found ask price: {ask_price}")
                        break

            if not ask_price:
                print(f"Could not find ask price for {metal_name}")
                return None

            # Get current time
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime("%b %d, %Y")
            time_str = now.strftime("%I:%M %p")

            return {
                'metal': metal_name.capitalize(),
                'date': date_str,
                'time': time_str,
                'bid': bid_price,
                'ask': ask_price
            }

        except Exception as e:
            print(f"Error fetching {metal_name} data: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def __del__(self):
        """Cleanup: Close the WebDriver when the scraper is destroyed."""
        if self.driver is not None:
            try:
                self.driver.quit()
                print("[DEBUG] Selenium WebDriver closed")
            except:
                pass

    def format_for_vestaboard(self, prices_data: Dict) -> str:
        """
        Format the prices data for display on Vestaboard.

        Args:
            prices_data: Dictionary containing Gold and Silver price data

        Returns:
            Formatted string suitable for Vestaboard display (6 rows max)
        """
        if not prices_data or prices_data.get('status') != 'success':
            return "Error fetching prices"

        data = prices_data.get('data', {})
        gold = data.get('gold', {})
        silver = data.get('silver', {})

        # Format the display text - keep it concise to fit in 6 rows
        # Parse the date to get month and day (e.g., "Oct 10, 2025" -> "October 10")
        date_str = gold.get('date', '')
        if date_str:
            # Extract month and day (remove year)
            date_parts = date_str.split(',')
            if len(date_parts) > 0:
                month_day = date_parts[0].strip()  # "Oct 10"

                # Spell out abbreviated months
                month_map = {
                    'Jan': 'January', 'Feb': 'February', 'Mar': 'March',
                    'Apr': 'April', 'May': 'May', 'Jun': 'June',
                    'Jul': 'July', 'Aug': 'August', 'Sep': 'September',
                    'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
                }

                for abbr, full in month_map.items():
                    if month_day.startswith(abbr):
                        month_day = month_day.replace(abbr, full, 1)
                        break

                date_str = month_day

        time_str = gold.get('time', '')
        datetime_display = f"{date_str} {time_str}".strip()

        lines = []
        lines.append(f"GOLD  BID:{gold.get('bid', 'N/A')}")
        lines.append(f"      ASK:{gold.get('ask', 'N/A')}")
        lines.append("")
        lines.append(f"SILVER BID:{silver.get('bid', 'N/A')}")
        lines.append(f"       ASK:{silver.get('ask', 'N/A')}")
        lines.append(datetime_display)

        return "\n".join(lines)
