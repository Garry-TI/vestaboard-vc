"""
Test script to verify that prices are actually updating and being sent to Vestaboard.
"""

from metals_scraper import MetalsScraper
from vestaboard_client import VestaboardClient
import time
import json

def test_price_updates():
    """Test that prices are fetched correctly and sent to Vestaboard."""
    print("Testing price updates...\n")

    scraper = MetalsScraper()

    # Fetch prices 3 times with 2 seconds between each fetch
    for i in range(3):
        print(f"\n--- Fetch #{i+1} at {time.strftime('%H:%M:%S')} ---")
        result = scraper.fetch_prices()

        if result['status'] == 'success':
            gold = result['data']['gold']
            silver = result['data']['silver']

            print(f"Gold Bid: {gold['bid']}, Ask: {gold['ask']}")
            print(f"Silver Bid: {silver['bid']}, Ask: {silver['ask']}")
            print(f"Timestamp: {gold['date']} {gold['time']}")

            print("\nFormatted message:")
            formatted = scraper.format_for_vestaboard(result)
            print(formatted)
            print(f"\nMessage length: {len(formatted)} characters")
        else:
            print(f"Error: {result['message']}")

        if i < 2:
            print("\nWaiting 2 seconds...")
            time.sleep(2)

    # Now test sending to Vestaboard
    print("\n\n=== Testing Vestaboard Send ===")
    try:
        client = VestaboardClient()
        print("Vestaboard client initialized")

        # Fetch fresh prices
        result = scraper.fetch_prices()
        if result['status'] == 'success':
            formatted = scraper.format_for_vestaboard(result)
            print(f"\nSending to Vestaboard:\n{formatted}")

            # Send using the client
            send_result = client.board.post(formatted)
            print(f"\nVestaboard response: {send_result}")

            # Read back what's on the board
            print("\nReading back from Vestaboard...")
            read_result = client.read_message()
            if read_result['status'] == 'success':
                print("Successfully read board data")
                print(f"Board data type: {type(read_result['data'])}")
            else:
                print(f"Error reading board: {read_result['message']}")
        else:
            print(f"Error fetching prices: {result['message']}")
    except Exception as e:
        print(f"Error with Vestaboard: {str(e)}")

if __name__ == "__main__":
    test_price_updates()
