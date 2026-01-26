"""Test canonical 000 import"""

try:
    from arifos.constitutional_core import Stage000Gate
    print("SUCCESS: Canonical import successful")
    
    gate = Stage000Gate()
    result = gate.execute('test_001', 'Hello world')
    print(f"RESULT: 000 execution: {result.verdict}")
    print(f"F12 score: {result.floor_scores['F12_Injection']:.2f}")
    print("All canonical modules working!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
