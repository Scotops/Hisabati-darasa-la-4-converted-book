import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def add_class(attrs, class_name):
    class_match = re.search(r'class="([^"]*)"', attrs, re.I | re.S)
    if class_match:
        classes = class_match.group(1).split()
        if class_name not in classes:
            classes.append(class_name)
        return attrs[:class_match.start(1)] + " ".join(classes) + attrs[class_match.end(1):]
    return attrs + f' class="{class_name}"'


def replace_row(filename, text_id, cells, rule=None):
    path = ROOT / filename
    page = path.read_text(encoding="utf-8")
    if f'data-metric-source="{text_id}"' in page:
        return
    pattern = re.compile(
        rf'<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*\bdata-id="{re.escape(text_id)}"[^>]*)>'
        rf'(?P<body>.*?)</(?P=tag)>',
        re.I | re.S,
    )
    match = pattern.search(page)
    if not match:
        raise RuntimeError(f"Could not find {text_id} in {filename}")
    attrs = re.sub(r'\s*data-id="[^"]+"', '', match.group("attrs"), count=1)
    attrs = add_class(attrs, "metric-inline-wrap")
    if rule:
        attrs = add_class(attrs, f"metric-inline-wrap--{rule}")
    width = "10rem" if len(cells) == 2 else "13.5rem"
    visible_cells = "".join(
        f'<span class="metric-inline-cell">{html.escape(str(value)) if value else "&nbsp;"}</span>'
        for value in cells
    )
    replacement = (
        f'<{match.group("tag")}{attrs} data-metric-source="{text_id}" '
        f'style="--metric-width:{width}">'
        f'<span class="sr-only" data-id="{text_id}">{match.group("body")}</span>'
        f'<span aria-hidden="true" class="metric-inline-row" style="--metric-cols:{len(cells)}">'
        f'{visible_cells}</span></{match.group("tag")}>'
    )
    path.write_text(page[:match.start()] + replacement + page[match.end():], encoding="utf-8")


page59 = {
    "pg059_n0009": ["km", "hm"],
    "pg059_n0010": ["8", "3"],
    "pg059_n0011": ["+ 6", "5"],
    "pg059_n0012": ["", "8"],
    "pg059_n0021": ["km", "hm"],
    "pg059_n0022": ["8", "3"],
    "pg059_n0023": ["+ 6", "5"],
    "pg059_n0024": ["14", "8"],
    "pg059_n0038": ["km", "hm"],
    "pg059_n0039": ["+1", ""],
    "pg059_n0040": ["7", "5"],
    "pg059_n0041": ["+ 4", "8"],
    "pg059_n0042": ["", "3"],
    "pg059_n0052": ["km", "hm"],
    "pg059_n0053": ["+1", ""],
    "pg059_n0054": ["7", "5"],
    "pg059_n0055": ["+ 4", "8"],
    "pg059_n0056": ["12", "3"],
}
for text_id, cells in page59.items():
    replace_row("pg059_sec001.html", text_id, cells)


page60_example = {
    "pg060_n0003": (["km", "hm", "dam"], None),
    "pg060_n0004": (["7", "4", "9"], None),
    "pg060_n0005": (["+ 6", "6", "3"], "double-rule"),
    "pg060_n0008": (["km", "hm", "dam"], None),
    "pg060_n0009": (["+1", "+1", ""], None),
    "pg060_n0010": (["7", "4", "9"], None),
    "pg060_n0011": (["+ 6", "6", "3"], "rule"),
    "pg060_n0012": (["14", "1", "2"], "rule"),
}
for text_id, (cells, rule) in page60_example.items():
    replace_row("pg060_sec001.html", text_id, cells, rule)

page60_path = ROOT / "pg060_sec001.html"
page60_html = page60_path.read_text(encoding="utf-8")
for text_id in page60_example:
    marker = f'data-metric-source="{text_id}"'
    marker_at = page60_html.find(marker)
    if marker_at < 0:
        raise RuntimeError(f"Could not left-align {text_id}")
    tag_start = page60_html.rfind("<", 0, marker_at)
    tag_end = page60_html.find(">", marker_at) + 1
    opening = page60_html[tag_start:tag_end]
    if "metric-inline-wrap--left" not in opening:
        opening = opening.replace("metric-inline-wrap", "metric-inline-wrap metric-inline-wrap--left", 1)
        page60_html = page60_html[:tag_start] + opening + page60_html[tag_end:]
page60_path.write_text(page60_html, encoding="utf-8")


page60_exercise = {
    "pg060_n0018": ["sm", "mm"], "pg060_n0019": ["13", "3"], "pg060_n0020": ["+ 5", "4"],
    "pg060_n0024": ["sm", "mm"], "pg060_n0025": ["1", "9"], "pg060_n0026": ["+ 3", "2"],
    "pg060_n0030": ["m", "dm", "mm"], "pg060_n0031": ["3", "6", "7"], "pg060_n0032": ["+ 7", "5", "9"],
    "pg060_n0036": ["km", "hm"], "pg060_n0037": ["5", "6"], "pg060_n0038": ["+ 2", "8"],
    "pg060_n0042": ["m", "sm", "mm"], "pg060_n0043": ["4", "25", "4"], "pg060_n0044": ["+ 6", "80", "8"],
    "pg060_n0048": ["km", "dam", "m"], "pg060_n0049": ["8", "9", "7"], "pg060_n0050": ["+ 5", "8", "4"],
    "pg060_n0054": ["km", "m", "sm"], "pg060_n0055": ["4", "40", "26"], "pg060_n0056": ["3", "22", "68"], "pg060_n0057": ["+ 5", "71", "23"],
    "pg060_n0061": ["km", "m"], "pg060_n0062": ["9", "56"], "pg060_n0063": ["+ 6", "48"],
    "pg060_n0067": ["dm", "sm", "mm"], "pg060_n0068": ["14", "4", "6"], "pg060_n0069": ["40", "8", "6"], "pg060_n0070": ["+ 12", "3", "1"],
}
for text_id, cells in page60_exercise.items():
    replace_row("pg060_sec002.html", text_id, cells)


def place_page60_answers_on_lines():
    path = ROOT / "pg060_sec002.html"
    page = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<div class="mt-5 border-b-2 border-neutral-500 pb-1">'
        r'<span data-id="(?P<empty_id>pg060_n\d+)"></span></div>\s*'
        r'</div>\s*'
        r'<input class="(?P<classes>[^"]*)"(?P<attrs>[^>]*)>',
        re.I | re.S,
    )

    def replacement(match):
        classes = " ".join(
            name for name in match.group("classes").split()
            if name not in {"mt-2", "w-full", "bg-transparent", "text-center", "outline-none"}
        )
        return (
            '<label class="metric-answer-slot">'
            f'<span class="sr-only" data-id="{match.group("empty_id")}"></span>'
            f'<input class="metric-answer-input {classes}"{match.group("attrs")}>'
            '</label>'
            '</div>'
        )

    page, count = pattern.subn(replacement, page)
    if count not in (0, 9):
        raise RuntimeError(f"Expected 9 answer slots, changed {count}")
    path.write_text(page, encoding="utf-8")


place_page60_answers_on_lines()


def place_page63_answers_on_lines():
    path = ROOT / "pg063_sec002.html"
    page = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<div class="mt-10 border-t-\[3px\] border-gray-500 w-\[72%\] max-sm:w-\[68%\]"></div>'
        r'<input class="(?P<classes>[^"]*)"(?P<attrs>[^>]*)>',
        re.I | re.S,
    )

    def replacement(match):
        classes = " ".join(
            name for name in match.group("classes").split()
            if name not in {
                "mt-2", "w-[72%]", "max-sm:w-[68%]", "bg-transparent",
                "border-0", "outline-none", "text-center", "p-0", "block",
            }
        )
        return (
            '<label class="metric-answer-slot metric-answer-slot--exercise">'
            f'<input class="metric-answer-input {classes}"{match.group("attrs")}>'
            '</label>'
        )

    page, count = pattern.subn(replacement, page)
    if count not in (0, 9):
        raise RuntimeError(f"Expected 9 page 63 answer slots, changed {count}")
    page = page.replace(
        "./assets/book-quality.css?v=10", "./assets/book-quality.css?v=14"
    )
    path.write_text(page, encoding="utf-8")


place_page63_answers_on_lines()


for filename in ("pg059_sec001.html", "pg060_sec001.html", "pg060_sec002.html"):
    path = ROOT / filename
    page = path.read_text(encoding="utf-8").replace(
        "./assets/book-quality.css?v=10", "./assets/book-quality.css?v=12"
    ).replace(
        "./assets/book-quality.css?v=11", "./assets/book-quality.css?v=12"
    ).replace(
        "./assets/book-quality.css?v=12", "./assets/book-quality.css?v=13"
    )
    path.write_text(page, encoding="utf-8")

print(f"Aligned {len(page59) + len(page60_example) + len(page60_exercise)} metric rows.")
