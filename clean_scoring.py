import os

# path to your scoring.py
path = os.path.join(os.path.dirname(__file__), "tracker", "scoring.py")

# read as raw bytes, strip all 0x00 nulls, write back
with open(path, "rb") as f:
    data = f.read()

clean = data.replace(b'\x00', b'')

with open(path, "wb") as f:
    f.write(clean)

print("✅ scoring.py cleaned of null bytes")