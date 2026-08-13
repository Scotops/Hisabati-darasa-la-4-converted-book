import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content" / "i18n" / "sw-TZ"
texts_path = I18N / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
audios_path = I18N / "audios.json"
audios = json.loads(audios_path.read_text(encoding="utf-8"))
audio_keys_path = ROOT / "scripts" / "redo_audio_keys.txt"
audio_keys = {line.strip() for line in audio_keys_path.read_text(encoding="utf-8").splitlines() if line.strip()}
audio_keys.add("pg099_n0019")
audio_keys.update({"pg106_n0006", "pg106_n0018", "pg106_n0019"})
audio_keys.update(key for key in texts if key.startswith("pg133_"))
audio_keys.update(key for key in texts if key.startswith("pg135_"))
audio_keys.update(key for key in texts if key.startswith("pg159_"))


def replace_element_text(filename: str, text_id: str, new_text: str) -> None:
    path = ROOT / filename
    html = path.read_text(encoding="utf-8")
    pattern = re.compile(rf'(<[^>]+data-id="{re.escape(text_id)}"[^>]*>)(.*?)(</[^>]+>)', re.S)
    html, count = pattern.subn(lambda m: m.group(1) + new_text + m.group(3), html, count=1)
    if count != 1:
        raise RuntimeError(f"Expected one {text_id} element in {filename}; found {count}")
    path.write_text(html, encoding="utf-8")
    texts[text_id] = new_text
    audio_keys.add(text_id)


replace_element_text("pg046_sec002.html", "pg046_n0010", "561672 ÷ 696 =")
replace_element_text("pg177_sec002.html", "pg177_n0038", "sh 10 st 50 ÷ 5 =")
page183_vertical = {
    "pg183_n0028": "sh\n764\n× 6",
    "pg183_n0031": "sh      st\n5675    39\n× 8",
    "pg183_n0034": "sh      st\n190     90\n× 9",
    "pg183_n0037": "sh       st\n45330    80\n× 28",
    "pg183_n0040": "sh\n3500\n× 9",
    "pg183_n0043": "sh       st\n39850    77\n× 79",
    "pg183_n0046": "sh      st\n198     96\n× 69",
}
for key183, value183 in page183_vertical.items():
    replace_element_text("pg183_sec002.html", key183, value183)

# Validation page 118: restore the missing 5-by-7 fraction rectangle and
# shade three of its 35 equal parts for 1/5 × 3/7 = 3/35.
page118_path = ROOT / "pg118_sec002.html"
page118 = page118_path.read_text(encoding="utf-8")
if 'data-validation-fraction-rectangle="3-of-35"' not in page118:
    cells118 = "".join(
        '<span style="background:#53c7df"></span>' if index118 < 3 else '<span></span>'
        for index118 in range(35)
    )
    rectangle118 = (
        '<div aria-hidden="true" data-validation-fraction-rectangle="3-of-35" '
        'style="display:grid;grid-template-columns:repeat(7,2.25rem);grid-template-rows:repeat(5,1.35rem);'
        'width:max-content;max-width:100%;margin:1rem auto 1.25rem;border:2px solid #253247">'
        f'{cells118}</div>'
        '<style>[data-validation-fraction-rectangle="3-of-35"]>span{border-right:1px solid #64748b;'
        'border-bottom:1px solid #64748b}</style>'
    )
    page118, count118 = re.subn(
        r'(<p\b[^>]*data-id="pg118_n0042"[^>]*>.*?</p>)',
        r'\1' + rectangle118,
        page118,
        count=1,
        flags=re.DOTALL,
    )
    if count118 != 1:
        raise RuntimeError("Could not restore the page 118 fraction rectangle")
    page118_path.write_text(page118, encoding="utf-8")
replace_element_text(
    "pg058_sec001.html",
    "pg058_n0009",
    '<math><mrow><mi>m</mi><mtext>&#xa0;</mtext><mn>4000</mn><mo>=</mo>'
    '<mfrac><mrow><mi>m</mi><mtext>&#xa0;</mtext><mn>4000</mn><mo>×</mo>'
    '<mi>km</mi><mtext>&#xa0;</mtext><mn>1</mn></mrow>'
    '<mrow><mi>m</mi><mtext>&#xa0;</mtext><mn>1000</mn></mrow></mfrac></mrow></math>',
)

page71 = ROOT / "pg071_sec001.html"
html71 = page71.read_text(encoding="utf-8")
html71 = html71.replace(
    "grid grid-cols-3 max-sm:grid-cols-1 gap-x-8",
    "grid grid-cols-2 max-sm:grid-cols-1 gap-x-8",
)
html71 = html71.replace(
    '<div class="grid grid-cols-2 max-sm:grid-cols-1 gap-x-8',
    '<div style="width:min(100%,700px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-x-8',
)
html71 = html71.replace(
    'style="width:min(100%,900px);margin-inline:auto;grid-template-columns:repeat(2,minmax(0,1fr));" class="grid grid-cols-2 max-sm:grid-cols-1',
    'style="width:min(100%,700px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1',
)
page71.write_text(html71, encoding="utf-8")

texts["pg053_remember"] = "Jikumbushe"
audios.setdefault("pg053_remember", "pg053_remember.mp3")
audio_keys.add("pg053_remember")

page62_audio = {
    "pg062_audio_calc1": "Mpangilio wa kutoa: kilometa 12 meta 200, kutoa kilometa 4 meta 950.",
    "pg062_audio_step1": "1. Toa meta: m 200 – m 950, haitoshelezi. Chukua km1 sawa na m1000 kutoka km 12 na badili km 1 kuwa m 1000.",
    "pg062_audio_step2": "2. Jumlisha: m 200 + m 1000 = m 1200. Toa: m 1200 − m 950 = m 250. Andika 250 katika safu ya m. Safu ya km zimebaki km 11.",
    "pg062_audio_step3": "3. Toa, kilometa: km 11 – km 4 = km 7. Andika 7 katika safu ya km.",
    "pg062_audio_calc2": "Mpangilio wa kutoa: kilometa 10 meta 160 sentimeta 55, kutoa kilometa 4 meta 580 sentimeta 76.",
    "pg062_audio_step4": "1. Toa sentimeta: sm 55 – sm 76, haitoshelezi. Chukua m1 kutoka m 160 na badili m 1 kuwa sm 100. Jumlisha: sm100 + sm55 = sm 155. Toa: sm155 – sm76 = sm 79. Andika 79 katika safu ya sm. Safu ya meta zimebaki m 159. Kumbuka m 159 zimebakia katika safu ya meta.",
}
for key, value in page62_audio.items():
    texts[key] = value
    audios.setdefault(key, f"{key}.mp3")
    audio_keys.add(key)

# Validation row 22: page 74 questions 4–12 need real answer fields.
page74_path = ROOT / "pg074_sec001.html"
page74 = page74_path.read_text(encoding="utf-8")
page74 = page74.replace(
    'data-section-type="boxed_text" data-section-id="pg074_sec001"',
    'data-section-type="activity_fill_in_the_blank" data-section-id="pg074_sec001"',
)
# A data-id on the whole question makes the localization runtime replace all
# descendants (including inputs). Keep the ID on an sr-only narration span.
page74 = re.sub(
    r'<div data-id="([^"]+)" class="([^"]*min-h-\[260px\][^"]*)">',
    r'<div class="\2"><span class="sr-only" data-id="\1"></span>',
    page74,
)
answers74 = [
    "1 t 714 kg", "14 kg 40 dag", "2 kg 960 g",
    "9 t 806 kg 37 sg", "25 g 150 mg", "2 hg 95 g",
    "55 kg 28 sg 22 mg", "3 t 519 g 830 mg", "2 hg 50 g 8 sg",
]
for offset, answer in enumerate(answers74, start=4):
    old = '<div class="mt-14 border-t-2 border-gray-700"></div>'
    field = (
        f'<div class="mt-8 flex justify-center"><label class="sr-only" '
        f'for="pg074-answer-{offset}">Jibu la swali la {offset}</label>'
        f'<input id="pg074-answer-{offset}" class="w-full max-w-[220px] rounded-lg border-2 '
        f'border-emerald-400 bg-white px-3 py-2 text-center text-lg" '
        f'data-aria-id="aria-1-0-{offset - 4}" data-activity-item="item-{offset}" '
        f'aria-label="Jibu la swali la {offset}" tabindex="0" type="text"></div>'
    )
    if field not in page74:
        page74 = page74.replace(old, field, 1)
    page74 = page74.replace(
        f'data-activity-item="item-{offset}" aria-label="Jibu la swali la {offset}" type="text"',
        f'data-aria-id="aria-1-0-{offset - 4}" data-activity-item="item-{offset}" '
        f'aria-label="Jibu la swali la {offset}" tabindex="0" type="text"',
    )
answer_json = json.dumps(
    {f"item-{i}": answer for i, answer in zip(range(4, 13), answers74)},
    ensure_ascii=False,
)
marker74 = '    <div class="relative z-50" id="interface-container"></div>'
script74 = f'    <script>window.correctAnswers = {answer_json};</script>\n'
if "window.correctAnswers" not in page74:
    page74 = page74.replace(marker74, script74 + marker74)
page74_path.write_text(page74, encoding="utf-8")

# Validation row 24: rebuild page 78's image-only exercise as an accessible,
# narrated and checkable six-question activity.
page78_path = ROOT / "pg078_sec001.html"
page78 = page78_path.read_text(encoding="utf-8")
problems78 = [
    ("1", [("", "415", "205"), ("+", "27", "8")], "442 L 213 mL"),
    ("2", [("", "600", "40"), ("+", "350", "250")], "950 L 290 mL"),
    ("3", [("", "78", "426"), ("+", "55", "542")], "133 L 968 mL"),
    ("4", [("", "4", "750"), ("", "316", "250"), ("+", "15", "101")], "336 L 101 mL"),
    ("5", [("", "17", "800"), ("+", "3", "366")], "21 L 166 mL"),
    ("6", [("", "20", "920"), ("", "14", "112"), ("+", "13", "126")], "48 L 158 mL"),
]
cards78 = []
answers78 = {}
for number, rows, answer in problems78:
    key = f"pg078_ex_q{number}"
    spoken_rows = "; ".join(
        f"{'jumlisha ' if sign else ''}lita {litres}, mililita {millilitres}"
        for sign, litres, millilitres in rows
    )
    texts[key] = f"Swali la {number}: {spoken_rows}."
    audios.setdefault(key, f"{key}.mp3")
    audio_keys.add(key)
    row_html = "".join(
        f'<div>{sign}</div><div>{litres}</div><div>{millilitres}</div>'
        for sign, litres, millilitres in rows
    )
    cards78.append(
        f'<article class="rounded-2xl border border-pink-200 bg-white p-5 shadow-sm">'
        f'<span class="sr-only" data-id="{key}"></span>'
        f'<div class="flex items-start gap-4"><span class="text-2xl text-lime-600">{number}.</span>'
        f'<div class="mx-auto w-full max-w-[270px]"><div class="grid grid-cols-[2rem_1fr_1fr] '
        f'gap-x-4 text-center text-2xl leading-relaxed"><div></div><div>L</div><div>mL</div>{row_html}</div>'
        f'<div class="border-t-2 border-slate-700"></div>'
        f'<label class="sr-only" for="pg078-answer-{number}">Jibu la swali la {number}</label>'
        f'<input id="pg078-answer-{number}" data-aria-id="aria-1-0-{int(number)-1}" '
        f'data-activity-item="item-{number}" aria-label="Jibu la swali la {number}" tabindex="0" type="text" '
        f'class="mt-5 w-full rounded-lg border-2 border-emerald-400 px-3 py-2 text-center text-lg"></div></div></article>'
    )
    answers78[f"item-{number}"] = answer
section78 = (
    '<div class="container mx-auto max-w-6xl bg-white px-6 py-8 opacity-0" id="content">'
    '<section data-section-type="activity_fill_in_the_blank" data-section-id="pg078_sec001" class="mx-auto max-w-5xl">'
    '<h2 class="mb-8 rounded-3xl border-2 border-pink-500 bg-pink-100 px-6 py-3 text-3xl font-bold">Zoezi la kumi na moja</h2>'
    '<div class="grid grid-cols-3 gap-6 max-lg:grid-cols-2 max-sm:grid-cols-1">'
    + "".join(cards78) + '</div></section></div>'
)
page78 = re.sub(r'<div class="container content.*?</section></div>', section78, page78, count=1, flags=re.S)
marker78 = '    <div class="relative z-50" id="interface-container"></div>'
script78 = f'    <script>window.correctAnswers = {json.dumps(answers78, ensure_ascii=False)};</script>\n'
if "window.correctAnswers" not in page78:
    page78 = page78.replace(marker78, script78 + marker78)
page78_path.write_text(page78, encoding="utf-8")

# Validation row 26: the numbers in page 80 questions 10–12 were not keyed,
# so add complete mathematical narrations without changing visible wording.
page80_path = ROOT / "pg080_sec001.html"
page80 = page80_path.read_text(encoding="utf-8")
narrations80 = {
    "pg080_audio_q10": "Swali la kumi: lita 11 mililita 41, kutoa lita 8 mililita 74.",
    "pg080_audio_q11": "Swali la kumi na moja: lita 20 mililita 93, kutoa lita 16 mililita 37.",
    "pg080_audio_q12": "Swali la kumi na mbili: lita 90 mililita 180, kutoa lita 45 mililita 382.",
}
question_ids80 = ["pg080_n0004", "pg080_n0011", "pg080_n0018"]
for (key, spoken), question_id in zip(narrations80.items(), question_ids80):
    texts[key] = spoken
    audios.setdefault(key, f"{key}.mp3")
    audio_keys.add(key)
    anchor = f'<span data-id="{question_id}"'
    replacement = f'<span class="sr-only" data-id="{key}"></span>' + anchor
    if f'data-id="{key}"' not in page80:
        page80 = page80.replace(anchor, replacement, 1)
page80_path.write_text(page80, encoding="utf-8")

# Validation row 36: page 104 already labels dimensions on the arrows; remove
# the duplicate loose measurement pairs printed below each square.
page104_path = ROOT / "pg104_sec002.html"
page104 = page104_path.read_text(encoding="utf-8")
page104 = re.sub(
    r'\s*<div class="mt-3 flex justify-center gap-8 text-\[20px\] leading-none text-zinc-700 max-sm:text-\[18px\]">\s*'
    r'<span data-id="pg104_n0024">sm 8</span>\s*<span data-id="pg104_n0025">sm 8</span>\s*</div>',
    "",
    page104,
)
page104 = re.sub(
    r'\s*<div class="mt-3 flex justify-center gap-8 text-\[20px\] leading-none text-zinc-700 max-sm:text-\[18px\]">\s*'
    r'<span data-id="pg104_n0029">m 10</span>\s*<span data-id="pg104_n0030">m 10</span>\s*</div>',
    "",
    page104,
)
page104_path.write_text(page104, encoding="utf-8")

# Validation row 38: narrate the numerical structure of the fraction wall.
texts["pg115_im003_crop_v1"] = (
    "Chati ya sehemu. Mstari wa kwanza una moja nzima. Mistari inayofuata ina: "
    "nusu mbili, theluthi tatu, robo nne, moja ya tano mara tano, moja ya sita mara sita, "
    "moja ya saba mara saba, moja ya nane mara nane, moja ya tisa mara tisa, "
    "moja ya kumi mara kumi, moja ya kumi na moja mara kumi na moja, na moja ya kumi na mbili mara kumi na mbili."
)
audios["pg115_im003_crop_v1"] = "pg115_im003_crop_v1.mp3"
audio_keys.add("pg115_im003_crop_v1")

# Validation row 41: keep every vertically stacked fraction problem inside the
# viewport when the reader enlarges text.
page121_path = ROOT / "pg121_sec002.html"
page121 = page121_path.read_text(encoding="utf-8")
page121 = page121.replace(
    '<div class="grid grid-cols-3 gap-x-14 gap-y-12 max-lg:gap-x-8 max-lg:gap-y-10 max-sm:grid-cols-1 max-sm:gap-y-8">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-10">',
)
page121_path.write_text(page121, encoding="utf-8")

# Validation row 42: present Exercise 5 as one ordered vertical flow.
page123_path = ROOT / "pg123_sec001.html"
page123 = page123_path.read_text(encoding="utf-8")
page123 = page123.replace(
    '<div class="grid grid-cols-1 gap-x-10 gap-y-8 sm:grid-cols-2 lg:grid-cols-3">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-8">',
)
page123_path.write_text(page123, encoding="utf-8")

# Validation row 52: keep all vertical time calculations in view.
page155_path = ROOT / "pg155_sec001.html"
page155 = page155_path.read_text(encoding="utf-8")
page155 = page155.replace(
    '<div class="grid grid-cols-3 max-lg:grid-cols-2 max-sm:grid-cols-1 gap-x-16 gap-y-12 max-sm:gap-y-10">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-10">',
)
page155_path.write_text(page155, encoding="utf-8")

# Validation row 53: localization IDs on whole page-156 example cards were
# replacing all structured descendants. Retain them on narration-only spans.
page156_path = ROOT / "pg156_sec001.html"
page156 = page156_path.read_text(encoding="utf-8")
page156 = re.sub(
    r'<div data-id="(pg156_im[^"]+)" class="([^"]*max-w-5xl[^"]*)">',
    r'<div class="\2"><span class="sr-only" data-id="\1"></span>',
    page156,
)
page156_path.write_text(page156, encoding="utf-8")

# Validation row 54: separate hours from minutes and avoid clipped columns.
page157_path = ROOT / "pg157_sec002.html"
page157 = page157_path.read_text(encoding="utf-8")
page157 = page157.replace(
    '<div class="grid grid-cols-3 gap-x-12 gap-y-12 max-lg:grid-cols-2 max-lg:gap-x-10 max-lg:gap-y-10 max-sm:grid-cols-1 max-sm:gap-y-8">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-10">',
)
page157 = page157.replace(
    'grid-cols-[2ch_3ch] items-start justify-center gap-x-4',
    'grid-cols-[2ch_3ch] items-start justify-center gap-x-10',
)
page157_path.write_text(page157, encoding="utf-8")

# Validation row 58: rebuild page 162's text-only calculations as actual
# vertical hour/minute grids while preserving their narration IDs.
page162_path = ROOT / "pg162_sec001.html"
page162 = page162_path.read_text(encoding="utf-8")
page162 = page162.replace(
    '<div class="grid grid-cols-3 max-sm:grid-cols-1 gap-x-12 gap-y-8 max-sm:gap-y-6 mb-10">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-10 mb-10">',
)
problem_ids162 = [f"pg162_n{number:04d}" for number in range(6, 40, 3)]
for key in problem_ids162:
    value = re.sub(r"<[^>]+>", " ", texts.get(key, ""))
    match = re.search(r"saa\s+dakika\s+(\d+)\s+(\d+)\s+\D+\s*(\d+)\s+(\d+)", value)
    if not match:
        continue
    h1, m1, h2, m2 = match.groups()
    pattern = re.compile(rf'<span data-id="{key}" class="[^"]*">.*?</span>', re.S)
    visual = (
        f'<span class="sr-only" style="display:none!important" data-id="{key}"></span>'
        '<div style="display:grid;grid-template-columns:4rem 6rem;column-gap:2.5rem;width:max-content;margin-inline:auto" class="text-center text-[22px] leading-relaxed text-black">'
        f'<span>saa</span><span>dakika</span><span>{h1}</span><span>{m1}</span>'
        f'<span>− {h2}</span><span>{m2}</span></div>'
    )
    page162 = pattern.sub(visual, page162, count=1)
page162 = page162.replace(
    '<span class="sr-only" data-id="pg162_n',
    '<span class="sr-only" style="display:none!important" data-id="pg162_n',
)
page162 = page162.replace(
    '<div class="mx-auto grid w-fit grid-cols-[4rem_6rem] gap-x-10 text-center text-[22px] leading-relaxed text-black">',
    '<div style="display:grid;grid-template-columns:4rem 6rem;column-gap:2.5rem;width:max-content;margin-inline:auto" class="text-center text-[22px] leading-relaxed text-black">',
)
page162 = re.sub(
    r'(<span class="sr-only" style="display:none!important" data-id="pg162_n\d{4}"></span>)'
    r'<div style="display:grid;grid-template-columns:4rem 6rem;column-gap:2\.5rem;width:max-content;margin-inline:auto"[^>]*>.*?</div>',
    r'\1',
    page162,
    flags=re.S,
)
page162_path.write_text(page162, encoding="utf-8")

# Validation row 59: retain the calculation rule and input, remove the second
# decorative answer rule beneath questions 3–8.
page167_path = ROOT / "pg167_sec003.html"
page167 = page167_path.read_text(encoding="utf-8")
page167 = page167.replace(
    '<div class="border-t-2 border-gray-700 w-[145px] max-sm:w-[96px] mx-auto mt-1.5"></div>',
    "",
)
page167_path.write_text(page167, encoding="utf-8")

# Validation row 60: show questions 1–6 in an unclipped vertical flow.
page170_path = ROOT / "pg170_sec002.html"
page170 = page170_path.read_text(encoding="utf-8")
page170 = page170.replace(
    '<div class="grid grid-cols-3 max-sm:grid-cols-1 gap-x-10 max-lg:gap-x-6 gap-y-3 max-sm:gap-y-2">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-6">',
)
page170_path.write_text(page170, encoding="utf-8")

page177_q_path = ROOT / "pg177_sec001.html"
page177_q = page177_q_path.read_text(encoding="utf-8")
for number, dividend, divisor in (
    (7, "13440", "14"), (8, "33750", "45"),
    (9, "40640", "64"), (10, "468084", "57"),
):
    page177_q = page177_q.replace(
        f'aria-label="Jibu la swali la {number} sh {divisor}){dividend}"',
        f'aria-label="Jibu la swali la {number}: {dividend} gawanya kwa {divisor}"',
    )
page177_q_path.write_text(page177_q, encoding="utf-8")

# Validation row 64: exercise questions use an explicit division sign; reserve
# bracket notation for worked long-division methods.
page179_path = ROOT / "pg179_sec002.html"
page179 = page179_path.read_text(encoding="utf-8")
counter179 = 0
def replace_page179_question(match):
    global counter179
    counter179 += 1
    divisor, dividend, cents = match.groups()
    key = f"pg179_audio_div{counter179:02d}"
    value = f"sh {dividend} st {cents} ÷ {divisor} ="
    texts[key] = value
    audios[key] = f"{key}.mp3"
    audio_keys.add(key)
    return (
        '<tr><td colspan="2" class="py-2 text-center">'
        f'<span data-id="{key}">{value}</span></td></tr>'
    )
page179 = re.sub(
    r'<tr><td class="pr-8"><span class="border-t-2 border-slate-800 pl-1">(\d+)'
    r'<span class="pl-1">\)(\d+)</span></span></td><td>(\d+)</td></tr>',
    replace_page179_question,
    page179,
)
page179_path.write_text(page179, encoding="utf-8")

page183_path = ROOT / "pg183_sec002.html"
page183 = page183_path.read_text(encoding="utf-8")
page183 = page183.replace(
    '<div class="grid grid-cols-3 gap-x-16 gap-y-10 pt-10 max-lg:gap-x-8 max-lg:gap-y-8 max-sm:grid-cols-1 max-sm:pt-0 max-sm:gap-6">',
    '<div style="width:min(100%,760px);margin-inline:auto;grid-template-columns:minmax(0,1fr);" class="grid grid-cols-1 gap-y-8 pt-10 max-sm:pt-0">',
)
for key183, value183 in page183_vertical.items():
    visible183 = html.escape(value183, quote=True)
    replacement183 = (
        f'<label data-id="{key183}" data-display="{visible183}" '
        'style="display:block;font-size:0;margin-bottom:1.5rem"></label>'
    )
    page183, count183 = re.subn(
        rf'<label\b[^>]*\bdata-id="{re.escape(key183)}"[^>]*>.*?</label>',
        replacement183,
        page183,
        count=1,
        flags=re.DOTALL,
    )
    if count183 == 0:
        page183, count183 = re.subn(
            rf'<span\b[^>]*\bdata-id="{re.escape(key183)}"[^>]*>.*?</span>'
            rf'<div aria-hidden="true"[^>]*>.*?</div>',
            replacement183,
            page183,
            count=1,
            flags=re.DOTALL,
        )
    if count183 != 1:
        raise RuntimeError(f"Could not create aligned display for {key183}")
if 'label[data-display]::after' not in page183:
    page183 = page183.replace(
        '</style>',
        "\n      label[data-display]::after { content:attr(data-display); white-space:pre; display:block; font-family:monospace; text-align:right; width:11rem; max-width:100%; font-size:1.15rem; line-height:1.45; color:#222; }\n    </style>",
        1,
    )
page183_path.write_text(page183, encoding="utf-8")

texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audio_keys_path.write_text("\n".join(sorted(audio_keys)) + "\n", encoding="utf-8")
for html_path in ROOT.glob("*.html"):
    html = html_path.read_text(encoding="utf-8")
    updated = html.replace("book-quality.js?v=20", "book-quality.js?v=21")
    if updated != html:
        html_path.write_text(updated, encoding="utf-8")
print(f"Applied redo corrections; {len(audio_keys)} audio keys queued.")
