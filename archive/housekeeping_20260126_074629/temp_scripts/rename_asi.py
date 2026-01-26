"""
Rename asi_engine.py to asi_room.py
"""
import os

rooms_dir = "C:\\Users\\User\\arifOS\\canonical_core\\rooms"
old_path = os.path.join(rooms_dir, "asi_engine.py")
new_path = os.path.join(rooms_dir, "asi_room.py")

if os.path.exists(old_path):
    os.rename(old_path, new_path)
    print(f"Renamed: {old_path} → {new_path}")
else:
    print(f"ERROR: {old_path} not found")

# Verify
if os.path.exists(new_path):
    print("✅ Rename successful")
    print(f"File exists: {new_path}")
    print(f"File size: {os.path.getsize(new_path)} bytes")
else:
    print("❌ Rename failed")
