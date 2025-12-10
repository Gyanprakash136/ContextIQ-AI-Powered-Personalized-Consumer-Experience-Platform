import requests
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "mock_token"

def test_comprehensive():
    print("=" * 60)
    print("🔍 COMPREHENSIVE BUG DETECTION TEST")
    print("=" * 60)
    
    # Test 1: Basic Chat Response
    print("\n[TEST 1] Basic Chat Functionality")
    response = requests.post(
        f"{BASE_URL}/agent/chat",
        headers={"Authorization": f"Bearer {TOKEN}"},
        data={"message": "suggest nike basketball shoes under 5k", "user_id": "test_user"}
    )
    
    if response.status_code != 200:
        print(f"❌ CRITICAL: Chat endpoint failed with {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    print("✅ Chat endpoint responsive")
    
    # Test 2: Response Structure
    print("\n[TEST 2] Response Structure")
    required_fields = ["agent_response", "session_id", "products"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        print(f"❌ Missing fields: {missing}")
    else:
        print("✅ All required fields present")
    
    # Test 3: Link Detection in Text
    print("\n[TEST 3] Direct Links in Text Response")
    text = data.get("agent_response", "")
    
    # Check for markdown links
    import re
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
    
    if markdown_links:
        print(f"✅ Found {len(markdown_links)} markdown links in text")
        for i, (label, url) in enumerate(markdown_links[:3], 1):
            print(f"   {i}. [{label}]({url[:60]}...)")
            # Verify URL is valid
            if not url.startswith('http'):
                print(f"      ⚠️  WARNING: Link doesn't start with http")
    else:
        print("❌ NO markdown links found in text response")
        print(f"   Response preview: {text[:200]}")
    
    # Test 4: Product JSON Structure
    print("\n[TEST 4] Product JSON Structure")
    products = data.get("products", [])
    
    if not products:
        print("⚠️  No products in JSON (might be in text only)")
    else:
        print(f"✅ Found {len(products)} products in JSON")
        for i, p in enumerate(products[:2], 1):
            print(f"   Product {i}:")
            print(f"      Name: {p.get('name', 'N/A')}")
            print(f"      Price: {p.get('price', 'N/A')}")
            print(f"      Link: {p.get('link', 'N/A')[:60]}...")
            print(f"      Image: {p.get('image_url', 'N/A')[:60]}...")
            
            # Validate links
            link = p.get('link', '')
            if link and not link.startswith('http'):
                print(f"      ❌ INVALID LINK FORMAT")
    
    # Test 5: Image URLs
    print("\n[TEST 5] Image URL Validity")
    has_images = False
    for p in products:
        img = p.get('image_url', '')
        if img and img.startswith('http'):
            has_images = True
            break
    
    if has_images:
        print("✅ Valid image URLs found")
    else:
        print("⚠️  No valid image URLs in products")
    
    # Test 6: Predictive Insight
    print("\n[TEST 6] Predictive Insight")
    if "predictive_insight" in data and data["predictive_insight"]:
        print(f"✅ Predictive insight: {data['predictive_insight'][:80]}...")
    else:
        print("⚠️  No predictive insight")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Session ID: {data.get('session_id')}")
    print(f"Response Length: {len(text)} chars")
    print(f"Markdown Links: {len(markdown_links)}")
    print(f"Products in JSON: {len(products)}")
    print("=" * 60)

if __name__ == "__main__":
    test_comprehensive()
