import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "content" / "i18n" / "sw-TZ"
TEXTS_PATH = I18N / "texts.json"
AUDIOS_PATH = I18N / "audios.json"


def normalize_division(value: str) -> str:
    # Converter notation divisor)dividend is replaced by the mathematical division sign.
    return re.sub(r"(?<![\d,])(\d[\d,]*)\s*\)\s*(\d[\d,]*)(?!\s*\d)",
                  lambda m: f"{m.group(2)} \u00f7 {m.group(1)}", value)


texts = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
audios = json.loads(AUDIOS_PATH.read_text(encoding="utf-8"))
audio_keys = set()

division_pages = {44, 46, 47, 48, 49, 50}
for key, value in list(texts.items()):
    match = re.match(r"pg(\d{3})_", key)
    if match and int(match.group(1)) in division_pages and ")" in str(value):
        corrected = normalize_division(str(value))
        if corrected != value:
            texts[key] = corrected
            audio_keys.add(key)
            for html_path in ROOT.glob(f"pg{match.group(1)}_sec*.html"):
                html = html_path.read_text(encoding="utf-8")
                pattern = re.compile(rf'(<[^>]+data-id="{re.escape(key)}"[^>]*>)(.*?)(</[^>]+>)', re.S)
                html = pattern.sub(lambda m: m.group(1) + corrected + m.group(3), html)
                html_path.write_text(html, encoding="utf-8")
        elif "\u00f7" in str(value):
            audio_keys.add(key)

descriptions = {
    "pg078_im002": "Zoezi la kumi na moja lenye maswali sita ya kujumlisha lita na mililita kwa mpangilio wa wima.",
    "pg089_im002": "Mfano wa pili. Urefu wa upande mmoja wa bustani yenye umbo la mraba ni meta 13. Mzingo wake ni meta 13 mara 4, sawa na meta 52.",
    "pg089_im003_crop1": "Maumbo manne ya mraba yenye vipimo vya pande vilivyooneshwa.",
    "pg090_im005": "Pembetatu yenye pande zenye urefu wa sentimeta 6, sentimeta 7 na sentimeta 9.",
    "pg102_im005_seg001_v1_crop_v1_crop1_crop1": "Mstatili a wenye urefu wa meta 20 na upana wa meta 4.",
    "pg102_im005_seg002_v1_crop1": "Mstatili b wenye urefu wa sentimeta 18 na upana wa sentimeta 8.",
    "pg102_im006_crop1": "Mstatili c wenye urefu wa sentimeta 40 na upana wa sentimeta 15.",
    "pg102_im005_seg004_v1_crop_v1_crop1": "Mstatili d wenye urefu wa meta 39 na upana wa meta 17.",
    "pg115_im002": "Ukuta wa sehemu unaoonesha kitu kizima 1, kisha nusu, theluthi, robo, tano, sita, saba, nane, tisa, kumi, kumi na moja na kumi na mbili.",
    "pg091_desc001": "Pembetatu a ina pande za sentimeta 33, sentimeta 33 na sentimeta 27.",
    "pg091_desc002": "Pembetatu b ina pande za meta 3, meta 5 na meta 4.",
    "pg091_desc003": "Pembetatu c ina pande za meta 34, meta 32 na meta 34.",
    "pg091_desc004": "Pembetatu d ina pande tatu zenye sentimeta 54 kila upande.",
    "pg120_desc001": "Mchoro wa mstatili uliogawanywa katika miraba 12. Miraba 6 imepakwa rangi kwa pamoja kuonesha sehemu 6 juu ya 12.",
    "pg120_desc002": "Mchoro wa mstatili uliogawanywa sehemu 8 sawa, sehemu 5 zimepakwa rangi kuonesha tano juu ya nane.",
    "pg120_desc003": "Mchoro wa mstatili uliogawanywa sehemu 4 sawa, sehemu 3 zimepakwa rangi kuonesha tatu juu ya nne.",
}
for key, value in descriptions.items():
    texts[key] = value
    audios.setdefault(key, f"{key}.mp3")
    audio_keys.add(key)

# Give every page-123 exercise expression a stable text/audio ID.
page123 = ROOT / "pg123_sec001.html"
html123 = page123.read_text(encoding="utf-8")
expression_pattern = re.compile(r'(<span class="text-black")(>)(.*?)(</span>)')
expression_index = 0
def tag_expression(match):
    global expression_index
    expression_index += 1
    key = f"pg123_ex{expression_index:03d}"
    visible = re.sub(r"&#x2044;", "/", match.group(3), flags=re.I)
    visible = re.sub(r"&#xd7;", "\u00d7", visible, flags=re.I)
    texts[key] = visible
    audios.setdefault(key, f"{key}.mp3")
    audio_keys.add(key)
    return f'{match.group(1)} data-id="{key}"{match.group(2)}{match.group(3)}{match.group(4)}'
if 'data-id="pg123_ex001"' not in html123:
    html123 = expression_pattern.sub(tag_expression, html123)
    page123.write_text(html123, encoding="utf-8")
for expression_index in range(1, 19):
    audio_keys.add(f"pg123_ex{expression_index:03d}")

# Re-record every text that contains a measurement abbreviation so the voice expands it.
unit_re = re.compile(r"(?:\b(?:km|sm|mm|mL|kg|hg|sh|st|m|L|g)\b|[\u00b2\u00b3])", re.I)
for key, value in texts.items():
    if key in audios and unit_re.search(str(value)):
        audio_keys.add(key)

TEXTS_PATH.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
AUDIOS_PATH.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "scripts" / "validation_round2_audio_keys.txt").write_text(
    "\n".join(sorted(audio_keys)) + "\n", encoding="utf-8")
for html_path in ROOT.glob("*.html"):
    html = html_path.read_text(encoding="utf-8")
    updated = html.replace("book-quality.js?v=19", "book-quality.js?v=20")
    if updated != html:
        html_path.write_text(updated, encoding="utf-8")
print(f"Updated division notation and prepared {len(audio_keys)} audio clips.")
