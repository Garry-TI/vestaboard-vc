"""
Vestaboard client wrapper for local API communication.
Handles reading and writing messages to the Vestaboard.
"""

import vestaboard
from typing import Optional, Dict, Any
from config import VESTABOARD_CONFIG
from metals_scraper import MetalsScraper


class VestaboardClient:
    """Wrapper class for Vestaboard operations."""

    def __init__(self, ip: str = None, api_key: str = None):
        """
        Initialize the Vestaboard client.

        Args:
            ip: IP address of the Vestaboard (defaults to config)
            api_key: Local API key (defaults to config)
        """
        self.ip = ip or VESTABOARD_CONFIG['ip']
        self.api_key = api_key or VESTABOARD_CONFIG['api_key']

        # Initialize the board connection with the API key
        self.board = vestaboard.Board(localApi={
            'ip': self.ip,
            'key': self.api_key
        })

        # Initialize the metals scraper
        self.metals_scraper = MetalsScraper()

    def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a text message to the Vestaboard.

        Args:
            message: Text message to display on the board

        Returns:
            Dictionary with status and message
        """
        try:
            self.board.post(message)
            return {
                'status': 'success',
                'message': f'Message sent successfully: {message[:50]}...' if len(message) > 50 else f'Message sent successfully: {message}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error sending message: {str(e)}'
            }

    def read_message(self) -> Dict[str, Any]:
        """
        Read the current message from the Vestaboard.

        Returns:
            Dictionary with status and current board content
        """
        try:
            current = self.board.read()
            return {
                'status': 'success',
                'data': current,
                'message': 'Message read successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error reading message: {str(e)}',
                'data': None
            }

    def send_raw(self, character_codes: list) -> Dict[str, Any]:
        """
        Send raw character codes to the Vestaboard.
        Allows precise control over each character position.

        Args:
            character_codes: 2D array of character codes (6 rows x 22 columns)

        Returns:
            Dictionary with status and message
        """
        try:
            self.board.raw(character_codes)
            return {
                'status': 'success',
                'message': 'Raw message sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error sending raw message: {str(e)}'
            }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the Vestaboard.

        Returns:
            Dictionary with connection status
        """
        try:
            # Try to read current state as a connection test
            result = self.read_message()
            if result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': f'Successfully connected to Vestaboard at {self.ip}'
                }
            else:
                return result
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            }

    def test_color_bits(self) -> Dict[str, Any]:
        """
        Test all color tiles on the Vestaboard.
        Cycles through character codes 63-71 (color tiles) for all positions.

        Returns:
            Dictionary with status and message
        """
        try:
            # Character codes 63-71 are the color tiles
            # 63: Red, 64: Orange, 65: Yellow, 66: Green, 67: Blue, 68: Violet, 69: White, 70: Black (blank), 71: Filled
            color_codes = list(range(63, 72))  # 63 through 71 inclusive

            # Vestaboard is 6 rows x 22 columns = 132 positions
            rows = 6
            cols = 22
            total_positions = rows * cols

            # Create a pattern that cycles through all color codes for all positions
            pattern = []
            code_index = 0

            for row in range(rows):
                row_data = []
                for col in range(cols):
                    # Cycle through color codes
                    row_data.append(color_codes[code_index % len(color_codes)])
                    code_index += 1
                pattern.append(row_data)

            # Send the pattern to the board
            self.board.raw(pattern)

            return {
                'status': 'success',
                'message': f'Color test pattern sent successfully! Displaying {len(color_codes)} color codes across all {total_positions} positions.'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error sending color test pattern: {str(e)}'
            }

    def display_metals_prices(self) -> Dict[str, Any]:
        """
        Fetch and display Gold and Silver prices on the Vestaboard.

        Returns:
            Dictionary with status and message
        """
        try:
            # Fetch prices from Kitco
            result = self.metals_scraper.fetch_prices()

            if result['status'] != 'success':
                return result

            # Format the prices for Vestaboard display
            message = self.metals_scraper.format_for_vestaboard(result)

            # Send to Vestaboard
            self.board.post(message)

            data = result.get('data', {})
            gold = data.get('gold', {})
            silver = data.get('silver', {})

            return {
                'status': 'success',
                'message': f'Prices displayed successfully!\nGold: Bid ${gold.get("bid")}, Ask ${gold.get("ask")}\nSilver: Bid ${silver.get("bid")}, Ask ${silver.get("ask")}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error displaying metals prices: {str(e)}'
            }
