import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def component(divisor, dividend):
    return (
        '<span aria-hidden="true" class="chapter-long-division">'
        f'<span class="chapter-long-division__divisor">{divisor}</span>'
        f'<span class="chapter-long-division__dividend">{dividend}</span>'
        '</span>'
    )


def replace_display(filename, text_id, divisor, dividend, question_number=None):
    path = ROOT / filename
    page = path.read_text(encoding="utf-8")
    existing_marker = f'data-long-division-source="{text_id}"'
    existing_start = page.find(existing_marker)
    existing_match = None
    if existing_start >= 0:
        opening_start = page.rfind("<", 0, existing_start)
        opening_end = page.find(">", existing_start) + 1
        opening = page[opening_start:opening_end]
        tag_match = re.match(r'<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*)>', opening, re.I | re.S)
        if not tag_match:
            raise RuntimeError(f"Could not parse existing {text_id} in {filename}")
        tag = tag_match.group("tag")
        token_pattern = re.compile(rf'<{tag}\b[^>]*>|</{tag}>', re.I | re.S)
        depth = 0
        closing_end = None
        for token in token_pattern.finditer(page, opening_start):
            depth += -1 if token.group(0).startswith("</") else 1
            if depth == 0:
                closing_end = token.end()
                break
        if closing_end is None:
            raise RuntimeError(f"Could not close existing {text_id} in {filename}")
        source_match = re.search(
            rf'<span class="sr-only" data-id="{re.escape(text_id)}">(?P<text>.*?)</span>',
            page[opening_start:closing_end],
            re.I | re.S,
        )
        if not source_match:
            raise RuntimeError(f"Could not recover narration text for {text_id} in {filename}")
        existing_match = (opening_start, closing_end, tag, tag_match.group("attrs"), source_match.group("text"))

    pattern = re.compile(
        rf'<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*\bdata-id="{re.escape(text_id)}"[^>]*)>'
        rf'(?P<body>.*?)</(?P=tag)>',
        re.I | re.S,
    )
    match = pattern.search(page) if existing_match is None else None
    if not match and existing_match is None:
        raise RuntimeError(f"Could not find {text_id} in {filename}")
    if existing_match:
        start, end, tag, attrs, source_text = existing_match
        attrs = re.sub(r'\s*data-long-division-source="[^"]+"', '', attrs, count=1)
    else:
        start, end, tag, attrs = match.start(), match.end(), match.group("tag"), match.group("attrs")
        attrs = re.sub(r'\s*data-id="[^"]+"', '', attrs, count=1)
        source_text = re.sub(r'<[^>]+>', ' ', match.group('body'))
        source_text = re.sub(r'\s+', ' ', source_text).strip()
    attrs = attrs.replace(" underline underline-offset-4", "")
    prefix = f'<span aria-hidden="true">{question_number}.</span>' if question_number else ''
    visible = component(divisor, dividend)
    wrapper_class = 'chapter-long-division-question' if question_number else ''
    replacement = (
        f'<{tag}{attrs} data-long-division-source="{text_id}">'
        f'<span class="sr-only" data-id="{text_id}">{source_text}</span>'
        f'<span class="{wrapper_class}">{prefix}{visible}</span>'
        f'</{tag}>'
    )
    page = page[:start] + replacement + page[end:]
    path.write_text(page, encoding="utf-8")


# Worked examples: both the presented calculation and the calculation shown
# under “Njia” use the same divisor-outside, dividend-under-the-bar notation.
worked = [
    ("pg043_sec001.html", "pg043_n0019", "2", "284"),
    ("pg043_sec001.html", "pg043_n0028", "2", "284"),
    ("pg043_sec001.html", "pg043_n0044", "12", "384"),
    ("pg043_sec001.html", "pg043_n0053", "12", "384"),
    ("pg045_sec001.html", "pg045_n0005", "3", "69"),
    ("pg045_sec001.html", "pg045_n0024", "80", "8080"),
    ("pg046_sec002.html", "pg046_n0010", "696", "561672"),
    ("pg048_sec001.html", "pg048_n0003", "12", "573"),
    ("pg048_sec001.html", "pg048_n0005", "12", "573"),
    ("pg048_sec001.html", "pg048_n0023", "23", "14262"),
    ("pg048_sec001.html", "pg048_n0025", "23", "14262"),
    ("pg049_sec001.html", "pg049_n0018", "7", "148"),
    ("pg049_sec001.html", "pg049_n0037", "27", "866"),
    ("pg050_sec001.html", "pg050_n0009", "8806", "880890"),
]
for args in worked:
    replace_display(*args)

# The final exercise group on page 44 is printed in long-division notation in
# the source book. Keep each original narration ID and the adjacent input.
page44_exercise = [
    ("pg044_n0061", "2", "64"),
    ("pg044_n0064", "3", "93"),
    ("pg044_n0067", "9", "999"),
    ("pg044_n0070", "8", "168"),
    ("pg044_n0073", "20", "400"),
    ("pg044_n0076", "7", "217"),
    ("pg044_n0079", "12", "264"),
    ("pg044_n0082", "31", "961"),
    ("pg044_n0085", "75", "825"),
]
for text_id, divisor, dividend in page44_exercise:
    replace_display("pg044_sec002.html", text_id, divisor, dividend)

# These exercise items were already written as divisor)dividend in the source,
# but lacked the top bar. Preserve their narration IDs while rendering the
# complete long-division symbol consistently.
exercise = [
    ("pg051_n0002", 13, "21", "25240"),
    ("pg051_n0003", 14, "35", "159610"),
    ("pg051_n0004", 15, "164", "527756"),
    ("pg051_n0005", 16, "11", "139"),
    ("pg051_n0006", 17, "1450", "72507"),
    ("pg051_n0007", 18, "14", "535"),
    ("pg051_n0008", 19, "28", "234"),
    ("pg051_n0009", 20, "200", "502808"),
]
for text_id, number, divisor, dividend in exercise:
    replace_display("pg051_sec001.html", text_id, divisor, dividend, number)

for filename in sorted({row[0] for row in worked} | {"pg044_sec002.html", "pg051_sec001.html"}):
    path = ROOT / filename
    page = path.read_text(encoding="utf-8").replace(
        "./assets/book-quality.css?v=10", "./assets/book-quality.css?v=11"
    )
    path.write_text(page, encoding="utf-8")

print(
    f"Standardized {len(worked) + len(page44_exercise) + len(exercise)} "
    "long-division displays across the division chapter."
)
