"""
Test script to analyze Kitco gold chart page structure.
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
    
    # Save the HTML to a file for inspection
    with open('kitco_gold_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("HTML saved to kitco_gold_page.html")
    
    # Look for tables
    print("\n=== Tables found ===")
    tables = soup.find_all('table')
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        print(f"Classes: {table.get('class')}")
        print(f"ID: {table.get('id')}")
        # Print first few rows
        rows = table.find_all('tr')[:3]
        for row in rows:
            print(f"  Row: {row.get_text(strip=True)[:100]}")
    
    # Look for divs with "gold" or "price" in class/id
    print("\n=== Divs with 'gold' or 'price' ===")
    divs = soup.find_all('div', class_=lambda x: x and ('gold' in str(x).lower() or 'price' in str(x).lower()))
    for i, div in enumerate(divs[:5]):
        print(f"\nDiv {i+1}:")
        print(f"Classes: {div.get('class')}")
        print(f"Text: {div.get_text(strip=True)[:150]}")
    
    # Look for text containing "Live Gold Price"
    print("\n=== Text containing 'Live Gold Price' ===")
    live_gold_elements = soup.find_all(text=lambda text: text and 'Live Gold Price' in text)
    for elem in live_gold_elements[:5]:
        print(f"Found: {elem.strip()}")
        print(f"Parent: {elem.parent.name}")
        print(f"Parent classes: {elem.parent.get('class')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
