import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pg017_sec001.html"
I18N = ROOT / "content" / "i18n" / "sw-TZ"
TEXTS = I18N / "texts.json"
AUDIOS = I18N / "audios.json"

upper_rows = [
    ("Numerali", ["50", "60", "70", "80", "90", "100"]),
    ("Namba za Kirumi", ["L", "LX", "LXX", "LXXX", "XC", "C"]),
    ("Namba kwa maneno", ["hamsini", "sitini", "sabini", "themanini", "tisini", "mia moja"]),
]
lower_rows = [
    ("LV", "hamsini na tano", "55"),
    ("LIX", "hamsini na tisa", "59"),
    ("LXXXIX", "themanini na tisa", "89"),
    ("LXXII", "sabini na mbili", "72"),
    ("XCIX", "tisini na tisa", "99"),
    ("LXIV", "sitini na nne", "64"),
    ("LVIII", "hamsini na nane", "58"),
    ("LXI", "sitini na moja", "61"),
    ("LXXIII", "sabini na tatu", "73"),
    ("LXXXV", "themanini na tano", "85"),
]

entries = {}


def tagged(tag, key, value, classes=""):
    entries[key] = value
    class_attr = f' class="{classes}"' if classes else ""
    return f'<{tag}{class_attr}><span data-id="{key}">{value}</span></{tag}>'


upper_html_rows = []
for row_index, (heading, values) in enumerate(upper_rows, start=1):
    cells = [tagged("th", f"pg017_tbl1_r{row_index}_c1", heading, "pg017-rowhead")]
    for column_index, value in enumerate(values, start=2):
        cells.append(tagged("td", f"pg017_tbl1_r{row_index}_c{column_index}", value))
    upper_html_rows.append("<tr>" + "".join(cells) + "</tr>")

upper_table = (
    '<div class="mb-6 overflow-x-auto">'
    '<table class="pg017-table" aria-label="Namba za Kirumi L hadi C">'
    '<tbody>' + "".join(upper_html_rows) + '</tbody></table></div>'
)

headers = ["Namba kwa Kirumi", "Namba kwa maneno", "Numerali"]
lower_head = "".join(
    tagged("th", f"pg017_tbl2_h{index}", value)
    for index, value in enumerate(headers, start=1)
)
lower_body = []
for row_index, row in enumerate(lower_rows, start=1):
    cells = "".join(
        tagged("td", f"pg017_tbl2_r{row_index}_c{column_index}", value)
        for column_index, value in enumerate(row, start=1)
    )
    lower_body.append("<tr>" + cells + "</tr>")

lower_table = (
    '<div class="mb-8 overflow-x-auto">'
    '<table class="pg017-table" aria-label="Mifano ya namba za Kirumi">'
    '<thead><tr>' + lower_head + '</tr></thead>'
    '<tbody>' + "".join(lower_body) + '</tbody></table></div>'
)

page = PAGE.read_text(encoding="utf-8")
old_upper = '''<div class="mb-6">
          <img data-id="pg017_im002_crop1" alt="Page background upper table" src="images/pg017_im002_crop1.png" class="block max-w-full h-auto mx-auto" style="max-width: 100%; height: auto;">
        </div>'''
old_lower = '''<div class="mb-8">
          <img data-id="pg017_im003" alt="Page background lower table" src="images/pg017_im003.png" class="block max-w-full h-auto mx-auto" style="max-width: 100%; height: auto;">
        </div>'''
if old_upper in page:
    page = page.replace(old_upper, upper_table, 1)
elif 'pg017_tbl1_r1_c1' not in page:
    raise RuntimeError("Upper page 17 table image was not found")
if old_lower in page:
    page = page.replace(old_lower, lower_table, 1)
elif 'pg017_tbl2_h1' not in page:
    raise RuntimeError("Lower page 17 table image was not found")

styles = '''
      .pg017-table { width:100%; max-width:100%; table-layout:fixed; border-collapse:collapse; color:#222; font-size:1.1rem; }
      .pg017-table th, .pg017-table td { border:1px solid #8fbe82; padding:.65rem .75rem; text-align:center; vertical-align:middle; }
      .pg017-table th { color:#6cad5b; font-weight:700; background:#fbfdf9; }
      .pg017-table .pg017-rowhead { text-align:left; width:20%; }
      @media (max-width:640px) { .pg017-table { font-size:.95rem; } .pg017-table th, .pg017-table td { padding:.45rem .5rem; } }
'''
if ".pg017-table" not in page:
    page = page.replace("    </style>", styles + "    </style>", 1)
PAGE.write_text(page, encoding="utf-8")

texts = json.loads(TEXTS.read_text(encoding="utf-8"))
audios = json.loads(AUDIOS.read_text(encoding="utf-8"))
texts.update(entries)
for key in entries:
    audios[key] = f"{key}.mp3?v=pg017-table-1"
TEXTS.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
AUDIOS.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

keys_path = ROOT / "scripts" / "pg017_audio_keys.txt"
keys_path.write_text("\n".join(["pg017_n0002", *entries.keys()]) + "\n", encoding="utf-8")
print(f"Converted both page 17 table images into semantic tables with {len(entries)} narrated cells.")
