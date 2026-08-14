import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "pg066_sec001.html"
I18N = ROOT / "content" / "i18n" / "sw-TZ"
SUMMARY_ID = "pg066_table_summary"
SUMMARY = (
    "Maelezo ya jedwali. Vipimo kutoka kidogo hadi kikubwa ni miligramu, "
    "sentigramu, desigramu, gramu, dekagramu, hektogramu na kilogramu. "
    "Kila kipimo kimoja ni sawa na vipimo kumi vya kitengo kilicho upande wake wa kushoto. "
    "Sentigramu 1 ni miligramu 10. Desigramu 1 ni sentigramu 10 au miligramu 100. "
    "Gramu 1 ni desigramu 10, sentigramu 100 au miligramu 1,000. "
    "Dekagramu 1 ni gramu 10. Hektogramu 1 ni dekagramu 10 au gramu 100. "
    "Kilogramu 1 ni hektogramu 10, dekagramu 100, gramu 1,000, desigramu 10,000, "
    "sentigramu 100,000 au miligramu 1,000,000. "
    "Ukihamia safu moja kwenda kulia, gawanya kwa 10. Ukihamia safu moja kwenda kushoto, zidisha kwa 10."
)


page = PAGE.read_text(encoding="utf-8")
table_start = page.index("            <table ")
table_end = page.index("            </table>", table_start) + len("            </table>")
table = page[table_start:table_end]

if f'data-id="{SUMMARY_ID}"' not in page:
    summary = (
        f'            <p id="pg066-table-description" class="sr-only" '
        f'data-id="{SUMMARY_ID}">{SUMMARY}</p>\n'
    )
    table = summary + table

table = table.replace(
    '<table class="',
    '<table aria-hidden="true" class="',
    1,
)
table = re.sub(r' data-id="pg066_n\d+"', "", table)
page = page[:table_start] + table + page[table_end:]
PAGE.write_text(page, encoding="utf-8")

texts_path = I18N / "texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts[SUMMARY_ID] = SUMMARY
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

audios_path = I18N / "audios.json"
audios = json.loads(audios_path.read_text(encoding="utf-8"))
audios[SUMMARY_ID] = f"{SUMMARY_ID}.mp3?v=accessible-table-1"
audios_path.write_text(json.dumps(audios, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Prepared the accessible narration for the page 66 weight table.")
