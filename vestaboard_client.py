"""
Vestaboard client wrapper for local API communication.
Handles reading and writing messages to the Vestaboard.
"""

import vestaboard
from typing import Optional, Dict, Any
from config import VESTABOARD_CONFIG
from metals_scraper import MetalsScraper

# Vestaboard supported characters mapping
# Any character not in this set will be replaced with blank (space)
VESTABOARD_CHARS = {
    # Letters (uppercase only)
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
    'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19,
    'T': 20, 'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26,
    # Numbers
    '1': 27, '2': 28, '3': 29, '4': 30, '5': 31, '6': 32, '7': 33, '8': 34, '9': 35, '0': 36,
    # Punctuation and symbols
    '!': 37, '@': 38, '#': 39, '$': 40, '(': 41, ')': 42, '-': 44, '+': 46,
    '&': 47, '=': 48, ';': 49, ':': 50, "'": 52, '"': 53, '%': 54, ',': 55,
    '.': 56, '/': 59, '?': 60, '°': 62,
    # Space (blank)
    ' ': 0
}

# Reverse mapping: character code to character
CODE_TO_CHAR = {code: char for char, code in VESTABOARD_CHARS.items()}

# Color tile codes and their colors
COLOR_TILES = {
    63: ('Red', '#FF0000'),
    64: ('Orange', '#FF8800'),
    65: ('Yellow', '#FFD700'),
    66: ('Green', '#00AA00'),
    67: ('Blue', '#0066FF'),
    68: ('Violet', '#8800FF'),
    69: ('White', '#FFFFFF'),
    70: ('Black', '#000000'),
    71: ('Filled', '#333333')
}


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

    def sanitize_message(self, message: str) -> str:
        """
        Sanitize message to only include Vestaboard-supported characters.
        Unsupported characters are replaced with spaces.

        Args:
            message: Input message string

        Returns:
            Sanitized message with only supported characters
        """
        sanitized = []
        replaced_chars = set()

        for char in message:
            # Convert lowercase to uppercase (Vestaboard only supports uppercase)
            upper_char = char.upper()

            # Check if character is supported
            if upper_char in VESTABOARD_CHARS:
                sanitized.append(upper_char)
            else:
                # Replace unsupported character with space
                sanitized.append(' ')
                if char not in ['\n', '\r', '\t']:  # Don't report whitespace replacements
                    replaced_chars.add(char)

        if replaced_chars:
            print(f"Note: Replaced unsupported characters: {', '.join(sorted(replaced_chars))}")

        return ''.join(sanitized)

    def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a text message to the Vestaboard.
        Automatically sanitizes message to replace unsupported characters.

        Args:
            message: Text message to display on the board

        Returns:
            Dictionary with status and message
        """
        try:
            # Sanitize the message before sending
            sanitized_message = self.sanitize_message(message)

            # Send to board
            self.board.post(sanitized_message)
            return {
                'status': 'success',
                'message': f'Message sent successfully: {sanitized_message[:50]}...' if len(sanitized_message) > 50 else f'Message sent successfully: {sanitized_message}'
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
                # If it's a timeout error, display the error message on Vestaboard
                if result.get('timeout'):
                    error_message = result['message']
                    self.board.post(error_message)
                    return {
                        'status': 'error',
                        'message': f'Timeout error displayed on Vestaboard: {error_message}'
                    }
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

    def generate_board_html(self, board_data) -> str:
        """
        Generate HTML representation of the Vestaboard display.

        Args:
            board_data: 2D array of character codes (6 rows x 22 columns)

        Returns:
            HTML string with styled Vestaboard grid
        """
        if not board_data or not isinstance(board_data, list):
            return "<div style='padding: 20px; text-align: center;'>No board data available</div>"

        html = """
        <style>
            .vestaboard-container {
                background-color: #1a1a1a;
                padding: 12px;
                border-radius: 8px;
                display: block;
                margin: 0 auto;
                width: fit-content;
                max-width: 100%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            .vestaboard-grid {
                display: grid;
                grid-template-columns: repeat(22, 27px);
                grid-template-rows: repeat(6, 34px);
                gap: 2px;
                background-color: #0a0a0a;
                padding: 5px;
                border-radius: 4px;
            }
            .vestaboard-tile {
                width: 27px;
                height: 34px;
                background-color: #000000;
                border: 1px solid #333;
                border-radius: 2px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Courier New', monospace;
                font-size: 18px;
                font-weight: bold;
                color: #FF8800;
                text-align: center;
            }
            .vestaboard-color-tile {
                border: none;
            }
        </style>
        <div class="vestaboard-container">
            <div class="vestaboard-grid">
        """

        for row in board_data:
            for code in row:
                if code in COLOR_TILES:
                    # Color tile
                    color_name, color_hex = COLOR_TILES[code]
                    html += f'<div class="vestaboard-tile vestaboard-color-tile" style="background-color: {color_hex};" title="{color_name}"></div>'
                else:
                    # Character tile
                    char = CODE_TO_CHAR.get(code, ' ')
                    # HTML escape special characters
                    if char == '<':
                        char = '&lt;'
                    elif char == '>':
                        char = '&gt;'
                    elif char == '&':
                        char = '&amp;'
                    elif char == ' ':
                        char = '&nbsp;'
                    
                    html += f'<div class="vestaboard-tile">{char}</div>'

        html += """
            </div>
        </div>
        """

        return html
