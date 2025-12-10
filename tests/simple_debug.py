import requests
import json

response = requests.post(
    "http://127.0.0.1:8000/agent/chat",
    headers={"Authorization": "Bearer mock_token"},
    data={"message": "suggest nike shoes under 5k", "user_id": "debug_user"}
)

print("Status Code:", response.status_code)
print("\nFull Response:")
print(json.dumps(response.json(), indent=2))
