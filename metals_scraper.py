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
            import json
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the __NEXT_DATA__ script tag containing JSON data
            next_data_script = soup.find('script', id='__NEXT_DATA__')
            if not next_data_script:
                print(f"Could not find __NEXT_DATA__ script for {metal_name}")
                return None

            # Parse the JSON data
            data = json.loads(next_data_script.string)

            # Navigate to the metal quote data
            queries = data.get('props', {}).get('pageProps', {}).get('dehydratedState', {}).get('queries', [])

            # Find the metalQuote query
            metal_data = None
            for query in queries:
                query_key = query.get('queryKey', [])
                if len(query_key) > 0 and query_key[0] == 'metalQuote':
                    metal_quote = query.get('state', {}).get('data', {}).get('GetMetalQuoteV3', {})
                    results = metal_quote.get('results', [])
                    if results:
                        metal_data = results[0]
                        break

            if not metal_data:
                print(f"Could not find metal quote data for {metal_name}")
                return None

            # Extract bid and ask prices
            bid_price = metal_data.get('bid')
            ask_price = metal_data.get('ask')

            if bid_price is None or ask_price is None:
                print(f"Could not find bid/ask prices for {metal_name}")
                return None

            # Format prices with commas for thousands
            bid_str = f"{bid_price:,.2f}"
            ask_str = f"{ask_price:,.2f}"

            # Get current time
            from datetime import datetime
            now = datetime.now()
            date_str = now.strftime("%b %d, %Y")
            time_str = now.strftime("%I:%M %p")

            return {
                'metal': metal_name.capitalize(),
                'date': date_str,
                'time': time_str,
                'bid': bid_str,
                'ask': ask_str
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
