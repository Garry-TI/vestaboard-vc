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
        self.url = "https://www.kitco.com/price/precious-metals"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_prices(self) -> Dict[str, any]:
        """
        Fetch Gold and Silver prices from Kitco.

        Returns:
            Dictionary containing price data for Gold and Silver
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table with precious metals prices
            prices = {
                'gold': self._extract_metal_data(soup, 'Gold'),
                'silver': self._extract_metal_data(soup, 'Silver')
            }

            # Validate that we got data
            if not prices['gold'] or not prices['silver']:
                return {
                    'status': 'error',
                    'message': 'Failed to extract price data from Kitco',
                    'data': None
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

    def _extract_metal_data(self, soup: BeautifulSoup, metal_name: str) -> Optional[Dict]:
        """
        Extract price data for a specific metal.

        Args:
            soup: BeautifulSoup object of the page
            metal_name: Name of the metal to extract (e.g., 'Gold', 'Silver')

        Returns:
            Dictionary with metal data or None if not found
        """
        try:
            # Find the desktop BidAskGrid list
            bid_ask_list = soup.find('ul', class_='BidAskGrid_listify__1liIU')

            if not bid_ask_list:
                return None

            # Find all list items (each metal is a list item)
            list_items = bid_ask_list.find_all('li')

            for item in list_items:
                # Find the gridifier div that contains the data
                gridifier = item.find('div', class_='BidAskGrid_gridifier__l1T1o')

                if not gridifier:
                    continue

                # Get all span elements in order
                spans = gridifier.find_all('span', recursive=False)

                if len(spans) < 5:
                    continue

                # First span contains the metal name (inside a link)
                metal_link = spans[0].find('a')
                if metal_link:
                    metal_text = metal_link.get_text(strip=True)
                else:
                    metal_text = spans[0].get_text(strip=True)

                # Check if this is the metal we're looking for
                if metal_name.lower() in metal_text.lower():
                    # Extract the data
                    date = spans[1].get_text(strip=True)
                    time = spans[2].get_text(strip=True)
                    bid = spans[3].get_text(strip=True)
                    ask = spans[4].get_text(strip=True)

                    return {
                        'metal': metal_text,
                        'date': date,
                        'time': time,
                        'bid': bid,
                        'ask': ask
                    }

            return None

        except Exception as e:
            print(f"Error extracting {metal_name} data: {str(e)}")
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
