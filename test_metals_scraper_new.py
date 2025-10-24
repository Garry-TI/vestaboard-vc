"""
Test the updated metals scraper.
"""

from metals_scraper import MetalsScraper

print("Testing updated MetalsScraper...")
print("=" * 60)

scraper = MetalsScraper()

print("\n1. Fetching prices from new Kitco sources...")
result = scraper.fetch_prices()

print(f"\nStatus: {result['status']}")
print(f"Message: {result['message']}")

if result['status'] == 'success':
    data = result['data']
    
    print("\n" + "=" * 60)
    print("GOLD DATA:")
    print("=" * 60)
    gold = data['gold']
    for key, value in gold.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("SILVER DATA:")
    print("=" * 60)
    silver = data['silver']
    for key, value in silver.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("VESTABOARD FORMATTED OUTPUT:")
    print("=" * 60)
    formatted = scraper.format_for_vestaboard(result)
    print(formatted)
    print("=" * 60)
else:
    print(f"\nError: {result.get('message', 'Unknown error')}")

print("\nTest complete!")
