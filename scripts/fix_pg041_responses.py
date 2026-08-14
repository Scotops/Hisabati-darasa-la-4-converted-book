import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pg041_sec001.html"
page = PAGE.read_text(encoding="utf-8")

# Question 16 belongs with the inline equations, but its original answer field
# was visually hidden. Keep the equation on one line and expose a real field.
page = page.replace(
    '<div class="flex items-baseline gap-3 text-[#222]">\n'
    '          <span class="min-w-[2.4rem] text-[1.25rem] leading-none text-[#76b260] max-sm:text-[0.95rem]"><span data-id="pg041_n0049">16.</span></span>\n'
    '          <label data-id="pg041_n0050" class="text-[1rem] leading-none max-sm:text-[0.9rem]">93115 &#xd7; 104 =</label>\n'
    '          <input class="sr-only" data-aria-id="aria-1-0-15" data-activity-item="item-16" aria-label="Jibu la swali la 16" tabindex="0" type="text">\n'
    '        </div>',
    '<div class="flex flex-wrap items-center gap-3 text-[#222]">\n'
    '          <span class="min-w-[2.4rem] text-[1.25rem] leading-none text-[#76b260] max-sm:text-[0.95rem]"><span data-id="pg041_n0049">16.</span></span>\n'
    '          <label data-id="pg041_n0050" class="whitespace-nowrap text-[1rem] leading-none max-sm:text-[0.9rem]">93115 &#xd7; 104 =</label>\n'
    '          <input style="width:min(100%,8rem);min-height:2.6rem" class="rounded-xl border-2 border-green-400 bg-white px-3 py-2 text-center text-base outline-none" data-aria-id="aria-1-0-15" data-activity-item="item-16" aria-label="Jibu la swali la 16" inputmode="numeric" autocomplete="off" tabindex="0" type="text">\n'
    '        </div>',
    1,
)

inline_questions = [
    (17, "pg041_n0052", "pg041_n0054", "7492", "pg041_n0055", "11", "aria-1-0-16"),
    (18, "pg041_n0058", "pg041_n0060", "165", "pg041_n0061", "21", "aria-1-0-17"),
    (19, "pg041_n0064", "pg041_n0066", "414", "pg041_n0067", "232", "aria-1-0-18"),
    (20, "pg041_n0070", "pg041_n0072", "79276", "pg041_n0073", "15", "aria-1-0-19"),
]
inline_cards = []
for number, number_id, left_id, left, right_id, right, aria_id in inline_questions:
    inline_cards.append(
        '<div class="flex flex-wrap items-center gap-3 rounded-2xl bg-white/55 px-4 py-4 text-[#222]">'
        f'<span class="min-w-[2.4rem] text-[1.25rem] leading-none text-[#76b260] max-sm:text-[0.95rem]"><span data-id="{number_id}">{number}.</span></span>'
        '<label class="whitespace-nowrap text-[1rem] leading-none max-sm:text-[0.9rem]">'
        f'<span data-id="{left_id}">{left}</span> '
        f'<span data-id="{right_id}">&#xd7; {right} =</span>'
        '</label>'
        f'<input style="width:min(100%,9rem);min-height:2.6rem" class="rounded-xl border-2 border-green-400 bg-white px-3 py-2 text-center text-base outline-none" data-aria-id="{aria_id}" data-activity-item="item-{number}" aria-label="Jibu la swali la {number}" inputmode="numeric" autocomplete="off" tabindex="0" type="text">'
        '</div>'
    )

replacement = (
    '<div class="mt-8 grid grid-cols-2 gap-5 max-sm:grid-cols-1 max-sm:gap-3" '
    'data-validation-inline-questions="16-20">'
    + "".join(inline_cards)
    + '</div>\n\n      <div class="mt-8 space-y-4 text-[#2a2a2a]">'
)
page, count = re.subn(
    r'<div class="mt-8 grid grid-cols-3 gap-x-12 gap-y-10.*?</div>\s*</div>\s*'
    r'<div class="mt-8 space-y-4 text-\[#2a2a2a\]">',
    replacement,
    page,
    count=1,
    flags=re.DOTALL,
)
if count != 1 and 'data-validation-inline-questions="16-20"' not in page:
    raise RuntimeError("Could not convert questions 17–20 to horizontal equations")

# At narrow widths the longer question 20 must not push its input onto a new
# line. Let the field flex into the remaining space instead of wrapping.
page = page.replace(
    'class="flex flex-wrap items-center gap-3 rounded-2xl bg-white/55 px-4 py-4 text-[#222]"',
    'class="flex items-center gap-3 rounded-2xl bg-white/55 px-4 py-4 text-[#222]"',
)
page = page.replace(
    'style="width:min(100%,9rem);min-height:2.6rem"',
    'style="flex:1 1 0;min-width:0;max-width:9rem;min-height:2.6rem"',
)
page = page.replace(
    'class="flex flex-wrap items-center gap-3 text-[#222]"',
    'class="flex items-center gap-3 text-[#222]"',
    1,
)
page = page.replace(
    'style="width:min(100%,8rem);min-height:2.6rem"',
    'style="flex:1 1 0;min-width:0;max-width:8rem;min-height:2.6rem"',
    1,
)

# Word problems 21–25 also had screen-reader-only textareas. Their answers are
# numeric, so expose full-width numeric fields that work on touch screens.
for item in range(21, 26):
    page = re.sub(
        rf'<textarea class="sr-only"([^>]*data-activity-item="item-{item}"[^>]*)></textarea>',
        rf'<input type="text" inputmode="numeric" autocomplete="off" style="display:block;width:100%;max-width:22rem;min-height:2.7rem;margin-top:.65rem" class="rounded-xl border-2 border-green-400 bg-white px-3 py-2 text-base outline-none"\1>',
        page,
        count=1,
    )

PAGE.write_text(page, encoding="utf-8")

# The runtime replaces inline fallback text from texts.json, so preserve the
# equals signs there as well and refresh the four affected narration clips.
i18n = ROOT / "content" / "i18n" / "sw-TZ"
texts_path = i18n / "texts.json"
audios_path = i18n / "audios.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
audios = json.loads(audios_path.read_text(encoding="utf-8"))
operator_text = {
    "pg041_n0055": "× 11 =",
    "pg041_n0061": "× 21 =",
    "pg041_n0067": "× 232 =",
    "pg041_n0073": "× 15 =",
}
texts.update(operator_text)
for key in operator_text:
    audios[key] = f"{key}.mp3?v=pg041-responsive-1"
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "scripts" / "pg041_audio_keys.txt").write_text("\n".join(operator_text) + "\n", encoding="utf-8")
print("Made page 41 answer controls responsive and changed questions 16–20 to horizontal equations.")
