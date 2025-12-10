import sys
sys.path.insert(0, '/Users/gyanprakash09/Developer/kpit/backend')

from core.agent_builder import build_contextiq_agent

# Build agent
print("Building agent...")
agent = build_contextiq_agent()

# Test run
print("\nRunning agent...")
response = agent.run(input=["User Message: Suggest nike shoes under 5k\n"], chat_history=[])

print("\n" + "="*60)
print("OUTPUT:")
print("="*60)
print(response.output[:500])
print("\n" + "="*60)
print(f"History length: {len(response.chat_history)}")
