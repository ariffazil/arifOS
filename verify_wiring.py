import arifos.core.metabolism as metabolism
import inspect

print("Verifying Active Sources...")
print(f"111 SENSE source: {inspect.getfile(metabolism.sense_111)}")
print(f"222 REFLECT source: {inspect.getfile(metabolism.reflect_222)}")
print(f"ALL EXPORTS: {metabolism.__all__}")
