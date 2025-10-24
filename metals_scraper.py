"""
Web scraper for Kitco precious metals prices.
Fetches Gold and Silver bid/ask prices from Kitco.com.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional


class MetalsScraper:
    """Scraper for Kitco precious metals prices."""

    def __init__(self):
        """Initialize the metals scraper."""
        self.gold_url = "https://www.kitco.com/charts/gold"
        self.silver_url = "https://www.kitco.com/charts/silver"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_prices(self) -> Dict[str, any]:
        """
        Fetch Gold and Silver prices from Kitco.

        Returns:
            Dictionary containing price data for Gold and Silver
        """
        try:
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

        except requests.RequestException as e:
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

    def _fetch_metal_from_chart(self, metal_name: str, url: str) -> Optional[Dict]:
        """
        Fetch price data for a specific metal from its chart page.

        Args:
            metal_name: Name of the metal (e.g., 'gold', 'silver')
            url: URL of the metal's chart page

        Returns:
            Dictionary with metal data or None if not found
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the bid price - it's in an h3 with specific classes
            bid_h3 = soup.find('h3', class_=lambda x: x and 'text-4xl' in x and 'font-bold' in x)
            if not bid_h3:
                print(f"Could not find bid price for {metal_name}")
                return None
            
            bid_price = bid_h3.get_text(strip=True)
            
            # Find the ask price - look for the "Ask" label and get the price next to it
            ask_price = None
            ask_divs = soup.find_all('div', class_=lambda x: x and 'text-sm' in str(x) and 'font-normal' in str(x))
            for ask_div in ask_divs:
                if 'Ask' in ask_div.get_text():
                    # The price is in the sibling div with text-[19px] class
                    parent = ask_div.parent
                    price_div = parent.find('div', class_=lambda x: x and 'text-[19px]' in str(x))
                    if price_div:
                        ask_price = price_div.get_text(strip=True)
                        break
            
            if not ask_price:
                print(f"Could not find ask price for {metal_name}")
                return None
            
            # Get current time (the page doesn't show explicit timestamp in the scraped section)
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
