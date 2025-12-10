import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/agent/chat"
HEADERS = {"Authorization": "Bearer mock_token"}

def test_scenario(name, message, expected_mode):
    print(f"\n--- Testing Scenario: {name} ---")
    payload = {"user_id": "test_auto", "message": message}
    try:
        start = time.time()
        # Add timeout of 60 seconds to prevent hanging forever
        response = requests.post(BASE_URL, headers=HEADERS, data=payload, timeout=60)
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: 200 OK ({duration:.2f}s)")
            
            # Helper to print truncated output
            resp_text = data.get('agent_response', '')[:100] + "..."
            products = data.get('products', [])
            
            print(f"Typical Response: {resp_text}")
            print(f"Products Found: {len(products)}")
            
            if expected_mode == "SHOPPING":
                if len(products) > 0:
                    print("✅ PASS: Products returned for shopping query.")
                    # Validate product structure
                    p = products[0]
                    if all(k in p for k in ["name", "price", "link"]):
                        print("✅ PASS: Product structure is valid (name, price, link).")
                    else:
                        print(f"❌ FAIL: Invalid product structure: {p.keys()}")
                else:
                    print("❌ FAIL: No products returned for shopping query!")
            
            elif expected_mode == "SUPPORT":
                if len(products) == 0:
                    print("✅ PASS: No products returned for support query.")
                else:
                    print(f"⚠️ COMPLIANCE: Valid but unexpected products for support: {len(products)}")
                    
        else:
            print(f"❌ FAIL: Status Code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    # 1. Standard Shopping (Nike)
    test_scenario("Shopping - Explicit", "I want to buy nike basketball shoes under 5000 inr", "SHOPPING")
    
    # 2. Support Query
    test_scenario("Support - Missing Order", "My order #12345 hasn't arrived yet. Where is it?", "SUPPORT")
    
    # 3. Ambiguous / General Info
    test_scenario("Info - Durex Brand", "Is Durex a good brand?", "SUPPORT") 
    # ^ Expecting text response, maybe no products unless specific
    
    # 4. No Results / Edge Case
    test_scenario("Edge - Non-existent", "Buy quantum levitation boots 5000 inr", "SHOPPING")
