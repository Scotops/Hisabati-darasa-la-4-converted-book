import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content" / "i18n" / "sw-TZ"
TEXTS_PATH = I18N / "texts.json"
AUDIOS_PATH = I18N / "audios.json"

texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
audios = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))


def set_text(key, value):
    texts[key] = value
    audios.setdefault(key, f"{key}.mp3")


def fraction(n, d):
    return f'<math><mfrac><mn>{n}</mn><mn>{d}</mn></mfrac></math>'


def update_answers(file_name, additions):
    path = ROOT / file_name
    source = path.read_text(encoding="utf-8")
    match = re.search(r"window\.correctAnswers\s*=\s*JSON\.parse\('([^']*)'\)", source)
    if not match:
        raise RuntimeError(f"No correctAnswers block in {file_name}")
    answers = json.loads(match.group(1))
    answers.update(additions)
    payload = json.dumps(answers, ensure_ascii=True, separators=(",", ":"))
    source = source[:match.start(1)] + payload + source[match.end(1):]
    path.write_text(source, encoding="utf-8")
    section = file_name.removesuffix(".html")
    for item, answer in additions.items():
        set_text(f"{section}_ans_{item}", str(answer))


# Restore missing answer controls and keys explicitly identified by validation.
pg032 = {
    "pg032_n0007": (1, 22 * 14), "pg032_n0010": (2, 28 * 18),
    "pg032_n0013": (3, 11 * 13), "pg032_n0016": (4, 24 * 19),
    "pg032_n0019": (5, 23 * 13), "pg032_n0022": (6, 33 * 33),
    "pg032_n0025": (7, 40 * 18), "pg032_n0028": (8, 42 * 12),
    "pg032_n0031": (9, 32 * 11), "pg032_n0034": (10, 41 * 22),
    "pg032_n0037": (11, 97 * 88), "pg032_n0040": (12, 85 * 60),
    "pg032_n0043": (13, 47 * 18), "pg032_n0046": (14, 53 * 34),
    "pg032_n0049": (15, 65 * 24),
}
for key, (item, answer) in pg032.items():
    value = re.sub(r"(?:\s*=\s*\[\[blank:item-\d+\]\])+\s*$", "", texts[key])
    set_text(key, f"{value} = [[blank:item-{item}]]")
update_answers("pg032_sec001.html", {f"item-{item}": str(answer) for item, answer in (v for v in pg032.values())})

pg038_ids = ["pg038_n0024", "pg038_n0028", "pg038_n0032", "pg038_n0036",
             "pg038_n0040", "pg038_n0044", "pg038_n0048", "pg038_n0052"]
for item, key in enumerate(pg038_ids, 7):
    value = re.sub(r"(?:\s*=\s*\[\[blank:item-\d+\]\])+\s*$", "", texts[key])
    set_text(key, f"{value} = [[blank:item-{item}]]")
update_answers("pg038_sec001.html", {"item-7": "2645939", "item-14": "57893868"})

pg041_ids = ["pg041_n0005", "pg041_n0008", "pg041_n0011", "pg041_n0014", "pg041_n0017",
             "pg041_n0020", "pg041_n0023", "pg041_n0026", "pg041_n0029", "pg041_n0032",
             "pg041_n0035", "pg041_n0038", "pg041_n0041", "pg041_n0044", "pg041_n0047"]
for item, key in enumerate(pg041_ids, 1):
    value = re.sub(r"(?:\s*=\s*\[\[blank:item-\d+\]\])+\s*$", "", texts[key])
    value = re.sub(r"\s*=\s*$", "", value)
    set_text(key, f"{value} = [[blank:item-{item}]]")

# Use the standard division sign rather than a long-division bracket in exercises.
for key in ["pg053_n0030", "pg053_n0032", "pg053_n0034", "pg053_n0036", "pg053_n0038",
            "pg053_n0040", "pg053_n0042", "pg053_n0044", "pg053_n0046", "pg053_n0048", "pg053_n0050"]:
    texts[key] = re.sub(r"(\d+)⟌(\d+)", r"\2 ÷ \1", texts[key])

# Correct fraction and formula notation called out by the reviewers.
set_text("pg106_n0006", f"{fraction(1, 2)} × kitako × kimo")
set_text("pg106_n0018", f"{fraction(1, 2)} × kitako × kimo")
set_text("pg106_n0019", f"= {fraction(1, 2)} × sm 10 × sm 7")
set_text("pg106_n0020", "= sm² 35")
set_text("pg106_n0021", "Kwa hiyo, eneo la pembetatu PQR ni sm² 35.")

set_text("pg127_n0011", f"{fraction(3, 8)} ÷ {fraction(4, 6)} =")
set_text("pg127_n0013", f"1. Badili kiasi na asili ya sehemu {fraction(4, 6)} inayogawanya; inakuwa {fraction(6, 4)}.")
set_text("pg127_n0014", f"2. Zidisha: {fraction(3, 8)} × {fraction(6, 4)} = {fraction(18, 32)}.")
set_text("pg127_n0015", f"= {fraction(9, 16)}")
set_text("pg127_n0016", f"Kwa hiyo, jibu ni {fraction(9, 16)}.")
set_text("pg127_n0021", f"{fraction(2, 5)} ÷ {fraction(1, 10)} = 4")
set_text("pg127_n0026", fraction(2, 5))

for key, n in [("pg133_n0003", 1), ("pg133_n0004", 1), ("pg133_n0012", 1),
               ("pg133_n0014", 2), ("pg133_n0016", 3), ("pg133_n0018", 4),
               ("pg133_n0020", 5), ("pg133_n0022", 6), ("pg133_n0024", 7),
               ("pg133_n0026", 8), ("pg133_n0028", 9)]:
    if key == "pg133_n0003":
        set_text(key, f"Kila sehemu inawakilisha {fraction(1, 10)} ya umbo zima.")
    elif key == "pg133_n0004":
        set_text(key, f"Sehemu iliyotiwa kivuli ni {fraction(1, 10)} na huandikwa 0.1 katika desimali.")
    else:
        set_text(key, fraction(n, 10))

set_text("pg137_n0037", "6 ÷ 10")
set_text("pg137_n0076", "1 ÷ 2")
set_text("pg138_n0032", "1 ÷ 100")
set_text("pg152_n0043", f"Gawanya dakika 15 kwa 60: 15 ÷ 60 = {fraction(15, 60)}")
set_text("pg152_n0044", f"Kwa hiyo, dakika 15 ni sawa na {fraction(15, 60)} ya saa.")

# Replace bracket-style division notation with explicit, pronounceable equations.
for key, dividend, divisor in [
    ("pg177_n0017", "13440", "14"), ("pg177_n0019", "33750", "45"),
    ("pg177_n0021", "40640", "64"), ("pg177_n0023", "468084", "57"),
    ("pg180_n0004", "133248 st 00", "24"), ("pg180_n0006", "144962 st 40", "16"),
    ("pg180_n0008", "75510 st 00", "25"), ("pg180_n0010", "133248 st 60", "12"),
    ("pg180_n0012", "653591 st 00", "15"), ("pg183_n0049", "sh 67678 st 52", "26"),
    ("pg183_n0052", "sh 45360 st 96", "6"),
]:
    set_text(key, f"{dividend} ÷ {divisor} =")

# Recover localized strings absent from the JSON and therefore skipped by read-aloud.
for path in ROOT.glob("pg*_sec*.html"):
    source = path.read_text(encoding="utf-8")
    for match in re.finditer(r'<(?P<tag>span|p|div|label|h[1-6]|td)[^>]*data-id="(?P<id>[^"]+)"[^>]*>(?P<body>.*?)</(?P=tag)>', source, re.S | re.I):
        key, body = match.group("id"), match.group("body")
        if key in texts or "data-id=" in body or re.search(r"<(?:input|textarea|select)\b", body, re.I):
            continue
        value = re.sub(r"<[^>]+>", " ", html.unescape(body))
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            set_text(key, value)
    for match in re.finditer(r'<img\b[^>]*data-id="(?P<id>[^"]+)"[^>]*alt="(?P<alt>[^"]*)"[^>]*>', source, re.I):
        key, alt = match.group("id"), html.unescape(match.group("alt")).strip()
        if key not in texts and alt and alt.lower() not in {"page background", key.lower()}:
            set_text(key, alt)

# The runtime renders these localized values into the matching data-id nodes.
# Keep authored HTML structures intact because many nodes contain MathML-like
# fraction spans whose visual layout must not be flattened into plain text.
TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
AUDIOS_PATH.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

heading_path = ROOT / "pg073_sec002.html"
heading_source = heading_path.read_text(encoding="utf-8")
heading_source = heading_source.replace(">zoezi la nne</p>", ">Zoezi la nane</p>")
heading_path.write_text(heading_source, encoding="utf-8")

# Some reader builds retain the inline fallback instead of replacing it from
# texts.json. Synchronize only reviewed leaf elements, never whole pages.
reviewed_ids = {
    "pg053_sec003.html": [f"pg053_n{n:04d}" for n in range(30, 51, 2)],
    "pg106_sec001.html": ["pg106_n0006", "pg106_n0018", "pg106_n0019", "pg106_n0020", "pg106_n0021"],
    "pg127_sec001.html": ["pg127_n0011", "pg127_n0013", "pg127_n0014", "pg127_n0015", "pg127_n0016", "pg127_n0021", "pg127_n0026"],
    "pg133_sec001.html": ["pg133_n0003", "pg133_n0004", "pg133_n0012", "pg133_n0014", "pg133_n0016", "pg133_n0018", "pg133_n0020", "pg133_n0022", "pg133_n0024", "pg133_n0026", "pg133_n0028"],
    "pg137_sec001.html": ["pg137_n0037", "pg137_n0076"],
    "pg138_sec001.html": ["pg138_n0032"],
    "pg152_sec001.html": ["pg152_n0043", "pg152_n0044"],
    "pg177_sec001.html": ["pg177_n0017", "pg177_n0019", "pg177_n0021", "pg177_n0023"],
    "pg180_sec001.html": ["pg180_n0004", "pg180_n0006", "pg180_n0008", "pg180_n0010", "pg180_n0012"],
    "pg183_sec002.html": ["pg183_n0049", "pg183_n0052"],
}
for file_name, ids in reviewed_ids.items():
    reviewed_path = ROOT / file_name
    reviewed_source = reviewed_path.read_text(encoding="utf-8")
    for key in ids:
        pattern = re.compile(rf'(?P<open><(?P<tag>span|p|div|label|h[1-6]|td)[^>]*data-id="{re.escape(key)}"[^>]*>)(?P<body>.*?)(?P<close></(?P=tag)>)', re.S | re.I)
        reviewed_source, count = pattern.subn(lambda match: match.group("open") + texts[key] + match.group("close"), reviewed_source, count=1)
        if count != 1:
            raise RuntimeError(f"Could not synchronize {key} in {file_name}")
    reviewed_path.write_text(reviewed_source, encoding="utf-8")

# Bust stale reader caches for the shared validation rules on every page.
for page_path in ROOT.glob("*.html"):
    page_source = page_path.read_text(encoding="utf-8")
    page_source = page_source.replace("book-quality.css?v=3", "book-quality.css?v=4")
    page_source = page_source.replace("book-quality.css?v=4", "book-quality.css?v=5")
    page_source = page_source.replace("book-quality.css?v=5", "book-quality.css?v=6")
    page_source = page_source.replace("book-quality.css?v=6", "book-quality.css?v=7")
    page_source = page_source.replace("book-quality.css?v=7", "book-quality.css?v=8")
    page_source = page_source.replace("book-quality.js?v=3", "book-quality.js?v=4")
    page_source = page_source.replace("book-quality.js?v=4", "book-quality.js?v=5")
    page_source = page_source.replace("book-quality.js?v=5", "book-quality.js?v=6")
    page_source = page_source.replace("book-quality.js?v=6", "book-quality.js?v=7")
    page_source = page_source.replace("book-quality.js?v=7", "book-quality.js?v=8")
    page_source = page_source.replace("book-quality.js?v=8", "book-quality.js?v=9")
    page_source = page_source.replace("book-quality.js?v=9", "book-quality.js?v=10")
    page_source = page_source.replace("book-quality.js?v=10", "book-quality.js?v=11")
    page_source = page_source.replace("book-quality.js?v=11", "book-quality.js?v=12")
    page_source = page_source.replace("book-quality.js?v=12", "book-quality.js?v=13")
    page_source = page_source.replace("book-quality.js?v=13", "book-quality.js?v=14")
    page_source = page_source.replace("book-quality.js?v=14", "book-quality.js?v=15")
    page_source = page_source.replace("book-quality.js?v=15", "book-quality.js?v=16")
    page_path.write_text(page_source, encoding="utf-8")

print(f"texts={len(texts)} audios={len(audios)}")
