"""
Test the Vestaboard metals display with the new scraper.
"""

from vestaboard_client import VestaboardClient

print("Testing Vestaboard metals price display...")
print("=" * 60)

client = VestaboardClient()

print("\nDisplaying metals prices on Vestaboard...")
result = client.display_metals_prices()

print(f"\nStatus: {result['status']}")
print(f"Message: {result['message']}")

if result['status'] == 'success':
    print("\n✓ Successfully sent metals prices to Vestaboard!")
else:
    print(f"\n✗ Error: {result['message']}")

print("\nTest complete!")
