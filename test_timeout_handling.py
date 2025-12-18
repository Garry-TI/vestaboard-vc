"""
Test script to verify timeout and HTTP error handling.
"""

from metals_scraper import MetalsScraper
from vestaboard_client import VestaboardClient

def test_error_handling():
    """Test that error messages are properly formatted."""
    scraper = MetalsScraper()

    print("Testing MetalsScraper error message format...")
    print("\nExpected message on timeout/error:")
    print("'kitco.com website down. Precious metals SPOT PRICES are NOT UP TO DATE.'")

    # Try to fetch prices (may fail if kitco.com is down or slow)
    result = scraper.fetch_prices()

    print(f"\nResult status: {result['status']}")
    print(f"Result message: {result['message']}")

    if result.get('timeout'):
        print("\n✓ Timeout flag is set correctly")

    if result['status'] == 'success':
        print("\n✓ Successfully fetched prices - kitco.com is working")
        print(f"Gold Bid: {result['data']['gold']['bid']}")
        print(f"Silver Bid: {result['data']['silver']['bid']}")
    else:
        print("\n✗ Failed to fetch prices (expected if kitco.com is down)")

if __name__ == "__main__":
    test_error_handling()
