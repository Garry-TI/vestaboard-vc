"""
Diagnostic script to test Vestaboard connection.
Run this to verify your configuration before using the main app.
"""

import vestaboard
from config import VESTABOARD_CONFIG

print("="*60)
print("Vestaboard Connection Test")
print("="*60)
print(f"\nIP Address: {VESTABOARD_CONFIG['ip']}")
print(f"API Key: {VESTABOARD_CONFIG['api_key'][:20]}...")
print("\nAttempting to connect...\n")

try:
    # Try creating the board with the local API config
    print("Creating Board object...")
    board = vestaboard.Board(localApi={
        'ip': VESTABOARD_CONFIG['ip'],
        'key': VESTABOARD_CONFIG['api_key']
    })

    print("Board object created successfully!")
    print("\nAttempting to send test message...")

    # Try sending a simple message
    board.post("Hello from Python!")

    print("SUCCESS! Message sent to Vestaboard!")
    print("\nConnection test passed!")

except Exception as e:
    print(f"ERROR: {str(e)}")
    print(f"\nFull error details:")
    import traceback
    traceback.print_exc()
    print("\nTroubleshooting steps:")
    print("1. Verify your Vestaboard is at IP: " + VESTABOARD_CONFIG['ip'])
    print("2. Check that the API key is correct in config.py")
    print("3. Ensure Local API is enabled on your Vestaboard")
    print("4. Try pinging the Vestaboard: ping " + VESTABOARD_CONFIG['ip'])

print("\n" + "="*60)
