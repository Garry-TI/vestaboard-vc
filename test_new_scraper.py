"""
Test the new Kitco gold chart scraper approach.
"""

import requests
from bs4 import BeautifulSoup

url = "https://www.kitco.com/charts/gold"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the bid price - it's in an h3 with specific classes
    bid_h3 = soup.find('h3', class_=lambda x: x and 'text-4xl' in x and 'font-bold' in x)
    if bid_h3:
        bid_price = bid_h3.get_text(strip=True)
        print(f"Gold Bid Price: {bid_price}")
    else:
        print("Could not find bid price")
    
    # Find the ask price - it's in a div with specific classes  
    # The ask section has "Ask" text followed by the price
    ask_divs = soup.find_all('div', class_=lambda x: x and 'text-sm' in str(x) and 'font-normal' in str(x))
    for ask_div in ask_divs:
        if 'Ask' in ask_div.get_text():
            # The price is in the next sibling div
            parent = ask_div.parent
            price_div = parent.find('div', class_=lambda x: x and 'text-[19px]' in str(x))
            if price_div:
                ask_price = price_div.get_text(strip=True)
                print(f"Gold Ask Price: {ask_price}")
                break
    
    # Try alternative approach - look for the ask price more broadly
    if not ask_price:
        # Look for divs with text-[19px] class
        price_divs = soup.find_all('div', class_=lambda x: x and 'text-[19px]' in str(x))
        print(f"\nFound {len(price_divs)} divs with text-[19px]:")
        for div in price_divs:
            print(f"  Content: {div.get_text(strip=True)}")
            print(f"  Classes: {div.get('class')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
