"""
Vestaboard client wrapper for local API communication.
Handles reading and writing messages to the Vestaboard.
"""

import vestaboard
from typing import Optional, Dict, Any
from config import VESTABOARD_CONFIG


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
