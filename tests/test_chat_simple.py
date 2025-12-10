import requests

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "mock_token"

def test_chat():
    print("🔹 Testing Chat Endpoint for Crash Fix...")
    response = requests.post(
        f"{BASE_URL}/agent/chat",
        headers={"Authorization": f"Bearer {TOKEN}"},
        data={"message": "Suggest basketball shoes", "user_id": "test_crash_fix"}
    )
    if response.status_code == 200:
        print("✅ Chat Success!")
        data = response.json()
        print(data)
        
        # Verify Links
        text = data.get("agent_response", "")
        if "http" in text or "www" in text:
            print("✅ Links detected in response!")
        else:
            print("❌ No links detected in response. Hallucination check failed?")
    else:
        print(f"❌ Chat Failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    test_chat()
