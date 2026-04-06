import re

filepath = r"C:\Users\User\arifOS\arifosmcp.transport\server.py"
with open(filepath, encoding="utf-8") as f:
    content = f.read()

repl = """"holding_reason": "Internal Engine Fracture",
            "error_class": e.__class__.__name__,
            "blast_radius": "kernel","""

content = re.sub(
    r'"holding_reason": "Internal Engine Fracture",(?!\s*"error_class")', repl, content
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated SABAR holding reasons!")
