import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.search_tool import search_web, GOOGLE_AVAILABLE, DDG_AVAILABLE

print(f"GOOGLE_AVAILABLE: {GOOGLE_AVAILABLE}")
print(f"DDG_AVAILABLE: {DDG_AVAILABLE}")

try:
    print("\n--- TEST SEARCH ---\n")
    results = search_web("iphone 15 price india")
    print(results)
except Exception as e:
    print(f"FATAL ERROR: {e}")
