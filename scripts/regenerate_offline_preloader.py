import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
target = root / "assets" / "offline-preloader.js"
source = target.read_text(encoding="utf-8")
prefix = "  var INLINE = "
start = source.index(prefix) + len(prefix)
end = source.index(";\n  var BASE_DIR", start)
inline = json.loads(source[start:end])

for key in list(inline):
    relative = key[2:] if key.startswith("./") else key
    path = root / relative
    if not path.is_file():
        continue
    if path.suffix.lower() == ".json":
        inline[key] = json.loads(path.read_text(encoding="utf-8"))
    elif path.suffix.lower() == ".html":
        inline[key] = path.read_text(encoding="utf-8")

payload = json.dumps(inline, ensure_ascii=False, separators=(",", ":"))
target.write_text(source[:start] + payload + source[end:], encoding="utf-8")
print(f"Regenerated {target.name} with {len(inline)} embedded resources.")
