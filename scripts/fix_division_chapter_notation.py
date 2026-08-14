import re
import json
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


def restore_plain_display(filename, text_id, text):
    """Restore a source expression that the printed book shows with an ordinary ÷."""
    path = ROOT / filename
    page = path.read_text(encoding="utf-8")
    marker = f'data-long-division-source="{text_id}"'
    marker_at = page.find(marker)
    if marker_at < 0:
        return
    start = page.rfind("<", 0, marker_at)
    opening_end = page.find(">", marker_at) + 1
    opening = page[start:opening_end]
    parsed = re.match(r'<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*)>', opening, re.I | re.S)
    if not parsed:
        raise RuntimeError(f"Could not parse {text_id} in {filename}")
    tag = parsed.group("tag")
    depth = 0
    end = None
    for token in re.finditer(rf'<{tag}\b[^>]*>|</{tag}>', page[start:], re.I | re.S):
        depth += -1 if token.group(0).startswith("</") else 1
        if depth == 0:
            end = start + token.end()
            break
    if end is None:
        raise RuntimeError(f"Could not close {text_id} in {filename}")
    attrs = re.sub(r'\s*data-long-division-source="[^"]+"', '', parsed.group("attrs"), count=1)
    replacement = f'<{tag}{attrs} data-id="{text_id}">{text}</{tag}>'
    path.write_text(page[:start] + replacement + page[end:], encoding="utf-8")


restore_plain_display("pg045_sec001.html", "pg045_n0005", "69 ÷ 3 =")


# Worked examples: both the presented calculation and the calculation shown
# under “Njia” use the same divisor-outside, dividend-under-the-bar notation.
worked = [
    ("pg043_sec001.html", "pg043_n0019", "2", "284"),
    ("pg043_sec001.html", "pg043_n0028", "2", "284"),
    ("pg043_sec001.html", "pg043_n0044", "12", "384"),
    ("pg043_sec001.html", "pg043_n0053", "12", "384"),
    ("pg045_sec001.html", "pg045_n0024", "80", "8080"),
    ("pg046_sec002.html", "pg046_n0010", "696", "561672", None, "561672 ÷ 696"),
    ("pg048_sec001.html", "pg048_n0003", "12", "573"),
    ("pg048_sec001.html", "pg048_n0005", "12", "573"),
    ("pg048_sec001.html", "pg048_n0023", "23", "14262"),
    ("pg048_sec001.html", "pg048_n0025", "23", "14262"),
    ("pg049_sec001.html", "pg049_n0018", "7", "148"),
    ("pg049_sec001.html", "pg049_n0037", "27", "866"),
    ("pg050_sec001.html", "pg050_n0009", "8806", "880890"),
    ("pg047_sec002.html", "pg047_n0029", "6", "82"),
    ("pg047_sec002.html", "pg047_n0032", "6", "82"),
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


def make_page47_interactive():
    path = ROOT / "pg047_sec001.html"
    page = path.read_text(encoding="utf-8").replace(
        'data-section-type="boxed_text" data-section-id="pg047_sec001"',
        'data-section-type="activity_fill_in_the_blank" data-section-id="pg047_sec001"',
    )
    answers = {
        10: "14", 11: "12", 12: "900", 13: "103", 14: "1814", 15: "121",
        16: "33", 17: "523", 18: "48", 19: "165", 20: "631", 21: "35",
        22: "386", 23: "2919", 24: "23", 25: "63", 26: "11", 27: "38",
    }
    for offset, (text_id, number, _, _) in enumerate(page47_exercise):
        pattern = re.compile(
            rf'<(?P<tag>p|label)\b(?P<attrs>[^>]*data-long-division-source="{text_id}"[^>]*)>'
            rf'(?P<body>.*?)</(?P=tag)>',
            re.I | re.S,
        )
        match = pattern.search(page)
        if not match:
            raise RuntimeError(f"Could not make {text_id} interactive")
        attrs = re.sub(
            r'class="[^"]*"',
            'class="flex min-w-0 flex-col items-start gap-3 text-lg leading-tight sm:text-2xl md:text-3xl"',
            match.group("attrs"),
            count=1,
        )
        answer_input = (
            f'<input type="text" class="h-12 w-full max-w-[13rem] rounded-lg border-2 '
            'border-gray-400 bg-white px-3 text-xl focus:border-cyan-600 focus:outline-none" '
            f'data-aria-id="aria-1-0-{offset}" data-activity-item="item-{number}" '
            f'aria-label="Jibu la swali la {number}" tabindex="0">'
        )
        replacement = f'<label{attrs}>{match.group("body")}{answer_input}</label>'
        page = page[:match.start()] + replacement + page[match.end():]

    answer_json = "{" + ",".join(
        f'\"item-{number}\":\"{answer}\"' for number, answer in answers.items()
    ) + "}"
    script = (
        '    <script type="text/javascript">\n'
        f"        window.correctAnswers = JSON.parse('{answer_json}');\n"
        '    </script>\n'
    )
    page = re.sub(
        r'\s*<script type="text/javascript">\s*window\.correctAnswers\s*=.*?</script>\s*',
        "\n" + script,
        page,
        flags=re.I | re.S,
    )
    if "window.correctAnswers" not in page:
        page = page.replace(
            '    <div class="relative z-50" id="interface-container"></div>',
            script + '    <div class="relative z-50" id="interface-container"></div>',
        )
    path.write_text(page, encoding="utf-8")


make_page47_interactive()

# Zoezi la tatu follows the mixed notation in the source: items 6 and 11 use
# an ordinary ÷ sign, while the remaining listed items use long division.
page48_exercise = [
    ("pg048_n0034", "3", "457"),
    ("pg048_n0037", "5", "99"),
    ("pg048_n0040", "9", "68"),
    ("pg048_n0043", "22", "938"),
    ("pg048_n0046", "12", "4005"),
    ("pg048_n0052", "610", "313252"),
    ("pg048_n0055", "43", "267"),
    ("pg048_n0058", "111", "2461"),
    ("pg048_n0061", "58", "4940"),
    ("pg048_n0067", "340", "1720"),
]
for text_id, divisor, dividend in page48_exercise:
    replace_display("pg048_sec002.html", text_id, divisor, dividend)

# The continuation on the next source page mixes short and long notation too.
for text_id, divisor, dividend in [
    ("pg049_n0007", "32", "3407"),
    ("pg049_n0013", "28", "20364"),
]:
    replace_display("pg049_sec001.html", text_id, divisor, dividend)

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


def replace_page50_work():
    """Replace the watermarked crop with an aligned, semantic long solution."""
    path = ROOT / "pg050_sec001.html"
    page = path.read_text(encoding="utf-8")
    visual = (
        '<div aria-hidden="true" class="chapter-long-division-work chapter-long-division-work--page50">'
        '<div class="chapter-long-division-work__quotient" data-math-value="100"></div>'
        '<div class="chapter-long-division-work__divisor" data-math-value="8806)"></div>'
        '<div class="chapter-long-division-work__dividend" data-math-value="880890"></div>'
        '<div class="chapter-long-division-work__step chapter-long-division-work__line" data-math-value="−8806"></div>'
        '<div class="chapter-long-division-work__step" data-math-value="2"></div>'
        '<div class="chapter-long-division-work__step chapter-long-division-work__line" data-math-value="−0↓"></div>'
        '<div class="chapter-long-division-work__step" data-math-value="29"></div>'
        '<div class="chapter-long-division-work__step chapter-long-division-work__line" data-math-value="−0↓"></div>'
        '<div class="chapter-long-division-work__step" data-math-value="290"></div>'
        '</div>'
    )
    replacement = (
        '<div class="w-full flex justify-start" data-long-division-work-source="pg050_im003_crop1">'
        '<span class="sr-only">Njia ya kugawanya 880890 kwa 8806, jibu ni 100 baki 290.</span>'
        f'{visual}</div>'
    )
    marker = 'data-long-division-work-source="pg050_im003_crop1"'
    marker_at = page.find(marker)
    if marker_at >= 0:
        start = page.rfind("<div", 0, marker_at)
        depth = 0
        end = None
        for token in re.finditer(r'<div\b[^>]*>|</div>', page[start:], re.I | re.S):
            depth += -1 if token.group(0).startswith("</") else 1
            if depth == 0:
                end = start + token.end()
                break
    else:
        match = re.search(r'<div class="w-full flex justify-start">\s*<img\b[^>]*pg050_im003_crop1[^>]*>\s*</div>', page, re.I | re.S)
        start, end = (match.start(), match.end()) if match else (None, None)
    if start is None or end is None:
        raise RuntimeError("Could not find pg050 worked-solution image")
    page = page[:start] + replacement + page[end:]
    path.write_text(page, encoding="utf-8")


replace_page50_work()


# Jikumbushe previously had no text IDs on its three statements, so read-aloud
# skipped them. Give each statement a stable text/audio key.
remember_texts = {
    "pg053_remember_1": "Namba inayogawanywa huitwa kigawanywe, ile inayogawa namba nyingine huitwa kigawanyo, na jawabu linalopatikana huitwa hisa.",
    "pg053_remember_2": "Hisa inaweza kuwa na baki au isiwe na baki.",
    "pg053_remember_3": "Katika kugawanya namba, anza kugawanya tarakimu za upande wa kushoto za kigawanywe kuelekea kulia.",
}
remember_path = ROOT / "pg053_sec001.html"
remember_page = remember_path.read_text(encoding="utf-8")
for key, value in remember_texts.items():
    if f'data-id="{key}"' not in remember_page:
        remember_page = remember_page.replace(f"<li>{value}</li>", f'<li data-id="{key}">{value}</li>')
if 'data-id="pg053_remember_1"' not in remember_page:
    remember_page = re.sub(
        r'<li>Namba inayogawanywa.*?</li>',
        f'<li data-id="pg053_remember_1">{remember_texts["pg053_remember_1"]}</li>',
        remember_page,
        count=1,
        flags=re.S,
    )
remember_path.write_text(remember_page, encoding="utf-8")

texts_path = ROOT / "content/i18n/sw-TZ/texts.json"
audios_path = ROOT / "content/i18n/sw-TZ/audios.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
audios = json.loads(audios_path.read_text(encoding="utf-8"))
for key, value in remember_texts.items():
    texts[key] = value
    audios[key] = f"{key}.mp3?v=chapter3-1"
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# In the review, questions 1–4 intentionally retain ÷; questions 5–15 use the
# long-division bracket shown in the original book.
page53_review = [
    ("pg053_n0030", "31", "161"),
    ("pg053_n0032", "760", "174800"),
    ("pg053_n0034", "90", "405000"),
    ("pg053_n0036", "998", "558880"),
    ("pg053_n0038", "95", "344"),
    ("pg053_n0040", "3500", "46163"),
    ("pg053_n0042", "55", "868230"),
    ("pg053_n0044", "1514", "113550"),
    ("pg053_n0046", "23", "575"),
    ("pg053_n0048", "2511", "37665"),
    ("pg053_n0050", "63", "204687"),
]
for text_id, divisor, dividend in page53_review:
    replace_display("pg053_sec003.html", text_id, divisor, dividend)


def make_page53_long_interactive():
    path = ROOT / "pg053_sec003.html"
    page = path.read_text(encoding="utf-8")
    for item, (text_id, _, _) in enumerate(page53_review, start=5):
        marker = f'data-long-division-source="{text_id}"'
        marker_at = page.find(marker)
        if marker_at < 0:
            raise RuntimeError(f"Could not find review item {item}")
        opening_start = page.rfind("<span", 0, marker_at)
        opening_end = page.find(">", marker_at) + 1
        opening = page[opening_start:opening_end].replace("fitb-sentence ", "")
        page = page[:opening_start] + opening + page[opening_end:]
        marker_at = page.find(marker, opening_start)
        opening_end = page.find(">", marker_at) + 1
        depth = 0
        closing_start = None
        for token in re.finditer(r'<span\b[^>]*>|</span>', page[opening_start:], re.I | re.S):
            depth += -1 if token.group(0).startswith("</") else 1
            if depth == 0:
                closing_start = opening_start + token.start()
                break
        if closing_start is None:
            raise RuntimeError(f"Could not close review item {item}")
        if f'data-activity-item="item-{item}"' not in page[opening_start:closing_start]:
            answer_input = (
                f'<input type="text" class="ml-3 h-10 w-28 rounded-lg border-2 border-gray-400 '
                f'bg-white px-2 text-lg focus:border-cyan-600 focus:outline-none" '
                f'data-activity-item="item-{item}" aria-label="Jibu la swali la {item}" tabindex="0">'
            )
            page = page[:closing_start] + answer_input + page[closing_start:]
    path.write_text(page, encoding="utf-8")


make_page53_long_interactive()

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
        "pg047_sec002.html",
        "pg048_sec002.html",
        "pg049_sec001.html",
        "pg050_sec001.html",
        "pg053_sec001.html",
        "pg053_sec003.html",
    }
):
    path = ROOT / filename
    page = path.read_text(encoding="utf-8").replace(
        "./assets/book-quality.css?v=10", "./assets/book-quality.css?v=11"
    )
    path.write_text(page, encoding="utf-8")

print(
    f"Standardized {len(worked) + len(page44_exercise) + len(page46_exercise) + len(page47_exercise) + len(page48_exercise) + 2 + len(page50_exercise) + len(exercise) + len(page53_review)} "
    "long-division displays across the division chapter."
)
