
import os
import pickle
from datetime import datetime

SESSION_DIR = "sessions"

if not os.path.exists(SESSION_DIR):
    print("No sessions directory found.")
    exit()

print(f"{'Session ID':<20} | {'User ID':<35} | {'Title':<30} | {'Updated At':<20}")
print("-" * 110)

for filename in os.listdir(SESSION_DIR):
    if filename.endswith(".pkl"):
        try:
            path = os.path.join(SESSION_DIR, filename)
            with open(path, "rb") as f:
                data = pickle.load(f)
                
            sid = data.get("session_id", "Unknown")
            uid = data.get("user_id", "None")
            title = data.get("title", "No Title")
            updated = data.get("updated_at", datetime.min)
            
            if isinstance(updated, str):
                updated_str = updated
            else:
                updated_str = updated.strftime("%Y-%m-%d %H:%M")
                
            print(f"{sid:<20} | {uid:<35} | {title[:28]:<30} | {updated_str:<20}")
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
