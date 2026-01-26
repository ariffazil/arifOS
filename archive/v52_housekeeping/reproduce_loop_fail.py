from arifos.core.floor_validators import validate_f4_clarity

# Scenario: AI gets stuck in a loop
loop_text = "I am processing the request. I am processing the request. I am processing the request. I am processing the request."
query = "What are you doing?"

context = {
    "response": loop_text
}

# Current validator only looks at query entropy!
# validate_f4_clarity(query: str, context: Dict[str, Any])
# The current implementation:
# query_entropy = len(query.split()) * 0.1
# clarity_gain = 1.0 if "?" in query else 0.5
# delta_s = query_entropy - clarity_gain
# pass = delta_s <= 0.0

result = validate_f4_clarity(query, context)
print(f"Loop Text: '{loop_text}'")
print(f"Result: {result}")

# We expect this to PASS (which is BAD) because it ignores the response content entirely.
if result['pass']:
    print("❌ FAILURE: System passed a repetitive loop.")
else:
    print("✅ SUCCESS: System caught the loop.")
