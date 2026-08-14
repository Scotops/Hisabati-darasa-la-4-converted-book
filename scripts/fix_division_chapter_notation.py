import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def component(divisor, dividend):
    return (
        '<span aria-hidden="true" class="chapter-long-division">'
        f'<span class="chapter-long-division__divisor" data-math-value="{divisor}"></span>'
        f'<span class="chapter-long-division__dividend" data-math-value="{dividend}"></span>'
        '</span>'
    )


def replace_display(filename, text_id, divisor, dividend, question_number=None, narration_text=None):
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
    if narration_text is not None:
        source_text = narration_text
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
    ("pg046_sec002.html", "pg046_n0010", "696", "561672", None, "561672 ÷ 696"),
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

# Long-method exercise pages use divisor-outside/dividend-under-the-bar
# notation in the printed book. The short-method exercises elsewhere in the
# chapter intentionally keep the ÷ sign.
page46_exercise = [
    ("pg046_n0019", "3", "723"),
    ("pg046_n0022", "605", "55055"),
    ("pg046_n0025", "78", "23400"),
    ("pg046_n0028", "926", "77784"),
    ("pg046_n0031", "25", "10000"),
    ("pg046_n0034", "6", "660"),
    ("pg046_n0037", "10", "356250"),
    ("pg046_n0040", "60", "66000"),
    ("pg046_n0043", "3512", "231792"),
]
for text_id, divisor, dividend in page46_exercise:
    replace_display("pg046_sec003.html", text_id, divisor, dividend)

page47_exercise = [
    ("pg047_n0002", 10, "9", "126"),
    ("pg047_n0003", 11, "4255", "51060"),
    ("pg047_n0004", 12, "812", "730800"),
    ("pg047_n0005", 13, "8", "824"),
    ("pg047_n0006", 14, "16", "29024"),
    ("pg047_n0007", 15, "7", "847"),
    ("pg047_n0008", 16, "27", "891"),
    ("pg047_n0009", 17, "124", "64852"),
    ("pg047_n0010", 18, "12", "576"),
    ("pg047_n0011", 19, "3", "495"),
    ("pg047_n0012", 20, "32", "20192"),
    ("pg047_n0013", 21, "2512", "87920"),
    ("pg047_n0014", 22, "75", "28950"),
    ("pg047_n0015", 23, "10", "29190"),
    ("pg047_n0016", 24, "34", "782"),
    ("pg047_n0017", 25, "364", "22932"),
    ("pg047_n0018", 26, "84", "924"),
    ("pg047_n0019", 27, "18", "684"),
]
for text_id, number, divisor, dividend in page47_exercise:
    replace_display("pg047_sec001.html", text_id, divisor, dividend, number)

page50_exercise = [
    ("pg050_n0019", "6", "467"),
    ("pg050_n0021", "1279", "255812"),
    ("pg050_n0023", "5", "327"),
    ("pg050_n0025", "25", "815"),
    ("pg050_n0027", "90", "405"),
    ("pg050_n0029", "251", "5397"),
    ("pg050_n0031", "104", "84765"),
    ("pg050_n0033", "43", "267"),
    ("pg050_n0035", "5850", "175594"),
    ("pg050_n0037", "48", "4954"),
    ("pg050_n0039", "32", "14498"),
    ("pg050_n0041", "12", "1235"),
]
for text_id, divisor, dividend in page50_exercise:
    replace_display("pg050_sec002.html", text_id, divisor, dividend)


def replace_page46_work():
    path = ROOT / "pg046_sec002.html"
    page = path.read_text(encoding="utf-8")
    page = page.replace(
        "Kwa hiyo, 561672&#xf7;696=807.",
        "Kwa hiyo, 561672 &#xf7; 696 = 807.",
    )
    visual = (
        '<div aria-hidden="true" class="chapter-long-division-work">'
        '<div class="chapter-long-division-work__quotient" data-math-value="807"></div>'
        '<div class="chapter-long-division-work__divisor" data-math-value="696)"></div>'
        '<div class="chapter-long-division-work__dividend" data-math-value="561672"></div>'
        '<div class="chapter-long-division-work__step chapter-long-division-work__line" data-math-value="−5568"></div>'
        '<div class="chapter-long-division-work__step" data-math-value="487"></div>'
        '<div class="chapter-long-division-work__step chapter-long-division-work__line" data-math-value="−000"></div>'
        '<div class="chapter-long-division-work__step" data-math-value="4872"></div>'
        '<div class="chapter-long-division-work__step chapter-long-division-work__line" data-math-value="−4872"></div>'
        '<div class="chapter-long-division-work__step" data-math-value="0"></div>'
        '</div>'
    )
    marker = 'data-long-division-work-source="pg046_n0012"'
    marker_at = page.find(marker)
    if marker_at >= 0:
        start = page.rfind("<div", 0, marker_at)
        token_pattern = re.compile(r'<div\b[^>]*>|</div>', re.I | re.S)
        depth = 0
        end = None
        for token in token_pattern.finditer(page, start):
            depth += -1 if token.group(0).startswith("</") else 1
            if depth == 0:
                end = token.end()
                break
        if end is None:
            raise RuntimeError("Could not close existing pg046_n0012 work")
        replacement = (
            '<div data-long-division-work-source="pg046_n0012">'
            '<span class="sr-only" data-id="pg046_n0012"></span>'
            f'{visual}</div>'
        )
        page = page[:start] + replacement + page[end:]
        path.write_text(page, encoding="utf-8")
        return
    pattern = re.compile(
        r'<p\b(?P<attrs>[^>]*\bdata-id="pg046_n0012"[^>]*)>.*?</p>',
        re.I | re.S,
    )
    match = pattern.search(page)
    if not match:
        raise RuntimeError("Could not find pg046_n0012 long-division work")
    attrs = re.sub(r'\s*data-id="pg046_n0012"', '', match.group("attrs"), count=1)
    replacement = (
        f'<div{attrs} data-long-division-work-source="pg046_n0012">'
        '<span class="sr-only" data-id="pg046_n0012"></span>'
        f'{visual}</div>'
    )
    page = page[:match.start()] + replacement + page[match.end():]
    path.write_text(page, encoding="utf-8")


replace_page46_work()

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

for filename in sorted(
    {row[0] for row in worked}
    | {
        "pg044_sec002.html",
        "pg046_sec003.html",
        "pg047_sec001.html",
        "pg050_sec002.html",
        "pg051_sec001.html",
    }
):
    path = ROOT / filename
    page = path.read_text(encoding="utf-8").replace(
        "./assets/book-quality.css?v=10", "./assets/book-quality.css?v=11"
    )
    path.write_text(page, encoding="utf-8")

print(
    f"Standardized {len(worked) + len(page44_exercise) + len(page46_exercise) + len(page47_exercise) + len(page50_exercise) + len(exercise)} "
    "long-division displays across the division chapter."
)
