# clean_encoding.py
import pathlib

path = pathlib.Path("tracker/scoring.py")
raw  = path.read_bytes()
clean = raw.replace(b"\x00", b"")              # remove all null bytes
path.write_text(clean.decode("utf-8", "replace"), encoding="utf-8")
print("scoring.py cleaned and re-saved as UTF-8.")