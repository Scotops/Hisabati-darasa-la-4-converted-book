import argparse
import asyncio
import html
import json
import re
import shutil
import time
from pathlib import Path

import edge_tts


VOICE = "sw-TZ-RehemaNeural"

SPEECH_OVERRIDES = {
    "pg017_n0002": "Namba za Kirumi, hamsini ya Kirumi hadi mia moja ya Kirumi",
    "pg017_tbl1_r2_c2": "hamsini ya Kirumi",
    "pg017_tbl1_r2_c3": "sitini ya Kirumi",
    "pg017_tbl1_r2_c4": "sabini ya Kirumi",
    "pg017_tbl1_r2_c5": "themanini ya Kirumi",
    "pg017_tbl1_r2_c6": "tisini ya Kirumi",
    "pg017_tbl1_r2_c7": "mia moja ya Kirumi",
    "pg017_tbl2_r1_c1": "hamsini na tano ya Kirumi",
    "pg017_tbl2_r2_c1": "hamsini na tisa ya Kirumi",
    "pg017_tbl2_r3_c1": "themanini na tisa ya Kirumi",
    "pg017_tbl2_r4_c1": "sabini na mbili ya Kirumi",
    "pg017_tbl2_r5_c1": "tisini na tisa ya Kirumi",
    "pg017_tbl2_r6_c1": "sitini na nne ya Kirumi",
    "pg017_tbl2_r7_c1": "hamsini na nane ya Kirumi",
    "pg017_tbl2_r8_c1": "sitini na moja ya Kirumi",
    "pg017_tbl2_r9_c1": "sabini na tatu ya Kirumi",
    "pg017_tbl2_r10_c1": "themanini na tano ya Kirumi",
    "pg066_n0010": "miligramu, em ge",
    "pg066_n0012": "sentigramu, es ge",
    "pg066_n0014": "desigramu, de ge",
    "pg066_n0016": "gramu, ge",
    "pg066_n0018": "dekagramu, de a ge",
    "pg066_n0020": "hektogramu, ha ge",
    "pg066_n0022": "kilogramu, ka ge",
    "pg078_ex_q1": "Swali la kwanza: lita mia nne na kumi na tano, mililita mia mbili na tano; jumlisha lita ishirini na saba, mililita nane.",
    "pg078_ex_q2": "Swali la pili: lita mia sita, mililita arobaini; jumlisha lita mia tatu na hamsini, mililita mia mbili na hamsini.",
    "pg078_ex_q3": "Swali la tatu: lita sabini na nane, mililita mia nne na ishirini na sita; jumlisha lita hamsini na tano, mililita mia tano na arobaini na mbili.",
    "pg078_ex_q4": "Swali la nne: lita nne, mililita mia saba na hamsini; lita mia tatu na kumi na sita, mililita mia mbili na hamsini; jumlisha lita kumi na tano, mililita mia moja na moja.",
    "pg078_ex_q5": "Swali la tano: lita kumi na saba, mililita mia nane; jumlisha lita tatu, mililita mia tatu na sitini na sita.",
    "pg078_ex_q6": "Swali la sita: lita ishirini, mililita mia tisa na ishirini; lita kumi na nne, mililita mia moja na kumi na mbili; jumlisha lita kumi na tatu, mililita mia moja na ishirini na sita.",
    "pg078_n0011": "Lita themanini, mililita mia tatu na sabini, kutoa lita arobaini na tano, mililita mia moja na sitini, ni sawa na.",
    "pg078_n0012": "Njia.",
    "pg078_n0013": "Safu za lita na mililita. Lita themanini, mililita mia tatu na sabini; toa lita arobaini na tano, mililita mia moja na sitini; jibu la mililita ni mia mbili na kumi.",
    "pg078_n0014": "Safu za lita na mililita. Lita themanini, mililita mia tatu na sabini; toa lita arobaini na tano, mililita mia moja na sitini; jibu ni lita thelathini na tano, mililita mia mbili na kumi.",
    "pg078_n0015": "Hatua.",
    "pg078_n0016": "Hatua ya kwanza. Toa mililita. Mililita mia tatu na sabini, kutoa mililita mia moja na sitini, ni sawa na mililita mia mbili na kumi. Andika mia mbili na kumi katika safu ya mililita.",
    "pg078_n0017": "Hatua ya pili. Toa lita. Lita themanini, kutoa lita arobaini na tano, ni sawa na lita thelathini na tano. Andika thelathini na tano katika safu ya lita.",
    "pg107_n0011": "Eneo la pembetatu ni sawa na moja ya mbili mara kitako mara kimo.",
    "pg107_n0012": "Ni sawa na moja ya mbili mara mita thelathini mara mita kumi na tano.",
    "pg108_n0002": "Ni sawa na sentimeta za mraba, ishirini na sita mara kumi na mbili, gawanya kwa mbili.",
    "pg108_n0003": "Ni sawa na sentimeta za mraba, mia tatu na kumi na mbili gawanya kwa mbili, ni sawa na sentimeta za mraba mia moja na hamsini na sita.",
    "pg108_n0004": "Kwa hiyo, eneo la pembetatu K L M ni sentimeta za mraba mia moja na hamsini na sita.",
    "pg121_n0022": "Swali la kwanza. mbili chini ya tano mara tatu chini ya saba ni sawa na",
    "pg121_n0023": "Swali la pili. sita chini ya tisa mara moja chini ya saba ni sawa na",
    "pg121_n0024": "Swali la tatu. mbili chini ya nne mara tatu chini ya tano ni sawa na",
    "pg121_n0025": "Swali la nne. tatu chini ya nane mara tano chini ya kumi ni sawa na",
    "pg121_n0026": "Swali la tano. kumi na tatu chini ya kumi na tano mara mbili chini ya nne ni sawa na",
    "pg121_n0027": "Swali la sita. saba chini ya kumi na mbili mara moja chini ya sita ni sawa na",
    "pg121_n0028": "Swali la saba. nne chini ya tano mara sita chini ya kumi na moja ni sawa na",
    "pg121_n0029": "Swali la nane. moja chini ya nne mara mbili chini ya saba ni sawa na",
    "pg121_n0030": "Swali la tisa. mbili chini ya tatu mara saba chini ya kumi ni sawa na",
    "pg121_n0031": "Swali la kumi. nane chini ya tisa mara moja chini ya tatu ni sawa na",
    "pg121_n0032": "Swali la kumi na moja. mbili chini ya tatu mara nne chini ya saba ni sawa na",
    "pg121_n0033": "Swali la kumi na mbili. kumi na moja chini ya kumi na tatu mara moja chini ya tano ni sawa na",
    "pg121_n0034": "Swali la kumi na tatu. tatu chini ya kumi na nne mara moja chini ya mbili ni sawa na",
    "pg121_n0035": "Swali la kumi na nne. tano chini ya tisa mara nne chini ya sita ni sawa na",
    "pg121_n0036": "Swali la kumi na tano. saba chini ya nane mara moja chini ya tano ni sawa na",
    "pg121_n0037": "Swali la kumi na sita. mbili chini ya kumi na moja mara nne chini ya tano ni sawa na",
    "pg121_n0038": "Swali la kumi na saba. tatu chini ya tano mara tano chini ya tisa ni sawa na",
    "pg121_n0039": "Swali la kumi na nane. tatu chini ya nne mara sita chini ya kumi ni sawa na",
    "pg132_im005": "Fikiri. Maisha bila matumizi ya namba za desimali.",
    "pg132_im006": "Mchoro una mstatili uliogawanywa katika sehemu kumi zilizo sawa. Kila sehemu ni moja chini ya kumi. Sehemu ya kwanza imewekewa kivuli; ni sawa na sifuri nukta moja.",
    "pg123_ex001": "sita mara tatu chini ya nne ni sawa na",
    "pg123_ex002": "mbili chini ya tatu mara tisa ni sawa na",
    "pg123_ex003": "tano chini ya sita mara thelathini ni sawa na",
    "pg123_ex004": "moja chini ya mbili mara ishirini na nne ni sawa na",
    "pg123_ex005": "ishirini na saba mara moja chini ya tisa ni sawa na",
    "pg123_ex006": "kumi na tano mara mbili chini ya tano ni sawa na",
    "pg123_ex007": "kumi na mbili mara moja chini ya sita ni sawa na",
    "pg123_ex008": "mbili chini ya kumi mara nne ni sawa na",
    "pg123_ex009": "tano chini ya tisa mara kumi na nane ni sawa na",
    "pg123_ex010": "ishirini na moja mara moja chini ya saba ni sawa na",
    "pg123_ex011": "moja chini ya tatu mara thelathini na sita ni sawa na",
    "pg123_ex012": "moja chini ya nane mara thelathini na mbili ni sawa na",
    "pg123_ex013": "tano mara moja chini ya sita ni sawa na",
    "pg123_ex014": "ishirini mara moja chini ya nne ni sawa na",
    "pg123_ex015": "moja chini ya kumi mara hamsini ni sawa na",
    "pg123_ex016": "tatu mara tatu chini ya kumi na moja ni sawa na",
    "pg123_ex017": "kumi na tatu mara moja chini ya kumi na tatu ni sawa na",
    "pg123_ex018": "arobaini mara moja chini ya ishirini ni sawa na",
}


def physical_audio_name(mapped_name):
    return mapped_name.split("?", 1)[0]


def roman_value(token):
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = previous = 0
    for character in reversed(token):
        value = values[character]
        total += -value if value < previous else value
        previous = max(previous, value)
    return str(total)


def swahili_number(value):
    units = ["sifuri", "moja", "mbili", "tatu", "nne", "tano", "sita", "saba", "nane", "tisa"]
    tens = {10: "kumi", 20: "ishirini", 30: "thelathini", 40: "arobaini",
            50: "hamsini", 60: "sitini", 70: "sabini", 80: "themanini", 90: "tisini"}
    if value < 10:
        return units[value]
    if value < 100:
        decade, unit = divmod(value, 10)
        base = tens[decade * 10]
        return base if unit == 0 else f"{base} na {units[unit]}"
    if value < 1000:
        hundred, remainder = divmod(value, 100)
        base = f"mia {units[hundred]}"
        return base if remainder == 0 else f"{base} na {swahili_number(remainder)}"
    scales = (
        (1_000_000_000, "bilioni"),
        (1_000_000, "milioni"),
        (100_000, "laki"),
        (1_000, "elfu"),
    )
    for divisor, name in scales:
        if value >= divisor:
            group, remainder = divmod(value, divisor)
            base = f"{name} {swahili_number(group)}"
            return base if remainder == 0 else f"{base} {swahili_number(remainder)}"
    raise ValueError(f"Namba hasi haitumiki hapa: {value}")


def spoken_number(token):
    normalized = token.replace(",", "")
    if "." not in normalized:
        return swahili_number(int(normalized))
    whole, decimal = normalized.split(".", 1)
    decimal_words = " ".join(swahili_number(int(digit)) for digit in decimal)
    return f"{swahili_number(int(whole))} nukta {decimal_words}"


def roman_spoken(token):
    return f"{swahili_number(int(roman_value(token)))} ya Kirumi"


def spoken_text(value):
    text = html.unescape(str(value))
    # Preserve the mathematical meaning of MathML square-unit notation before
    # tags are stripped. Otherwise m² is flattened to "m 2" and spoken wrongly.
    mathml_square_units = (
        (r"<math[^>]*>\s*<mrow[^>]*>\s*<mi[^>]*>m</mi>\s*<msup[^>]*>\s*<mi[^>]*>m</mi>\s*<mn[^>]*>2</mn>\s*</msup>\s*</mrow>\s*</math>", "milimeta za mraba"),
        (r"<math[^>]*>\s*<mrow[^>]*>\s*<mi[^>]*>s</mi>\s*<msup[^>]*>\s*<mi[^>]*>m</mi>\s*<mn[^>]*>2</mn>\s*</msup>\s*</mrow>\s*</math>", "sentimeta za mraba"),
        (r"<math[^>]*>\s*<msup[^>]*>\s*<mi[^>]*>m</mi>\s*<mn[^>]*>2</mn>\s*</msup>\s*</math>", "meta za mraba"),
    )
    for pattern, replacement in mathml_square_units:
        text = re.sub(pattern, replacement, text, flags=re.I | re.S)
    fraction = re.compile(r"<mfrac[^>]*>\s*<[^>]+>(.*?)</[^>]+>\s*<[^>]+>(.*?)</[^>]+>\s*</mfrac>", re.I | re.S)
    while fraction.search(text):
        text = fraction.sub(r" \1 chini ya \2 ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    # Expand mathematical and measurement abbreviations before converting digits.
    # Longer units must be replaced first so that, for example, m\u00b2 is not read as m.
    unit_patterns = (
        (r"\bmm\s*[\u00b2\u00b3]\b", {"\u00b2": "milimeta za mraba", "\u00b3": "milimeta za ujazo"}),
        (r"\bsm\s*[\u00b2\u00b3]\b", {"\u00b2": "sentimeta za mraba", "\u00b3": "sentimeta za ujazo"}),
        (r"\bm\s*[\u00b2\u00b3]\b", {"\u00b2": "meta za mraba", "\u00b3": "meta za ujazo"}),
    )
    for pattern, names in unit_patterns:
        text = re.sub(pattern, lambda match: names["\u00b2" if "\u00b2" in match.group(0) else "\u00b3"], text, flags=re.I)
    simple_units = (
        (r"\bmL\b", "mililita"), (r"\bkm\b", "kilomita"),
        (r"\bhm\b", "hektomita"),
        (r"\bsm\b", "sentimeta"), (r"\bmm\b", "milimeta"),
        (r"\bkg\b", "kilogramu"), (r"\bhg\b", "hektogramu"),
        (r"\bg\b", "gramu"), (r"\bL\b", "lita"),
        (r"\bsh\b", "shilingi"), (r"\bst\b", "senti"),
        (r"\bm\b", "mita"),
    )
    for pattern, replacement in simple_units:
        text = re.sub(pattern, replacement, text, flags=re.I)
    text = re.sub(r"\b[IVXLCDM]+\b", lambda match: roman_spoken(match.group(0)), text)
    text = re.sub(r"\[\[blank:item-\d+\]\]", " nafasi ya jibu ", text)
    text = re.sub(r"\d[\d,]*(?:\.\d+)?",
                  lambda match: spoken_number(match.group(0)), text)
    substitutions = {
        "×": " mara ", "÷": " gawanya kwa ", "−": " kutoa ", "-": " kutoa ",
        "×": " mara ", "÷": " gawanya kwa ", "−": " kutoa ",
        "\u00d7": " mara ", "\u00f7": " gawanya kwa ", "\u2212": " kutoa ", "/": " gawanya kwa ",
        "=": " ni sawa na ", "<": " ni ndogo kuliko ", ">": " ni kubwa kuliko ",
        "+": " jumlisha ", "%": " asilimia ",
    }
    for symbol, words in substitutions.items():
        text = text.replace(symbol, words)
    return re.sub(r"\s+", " ", text).strip()


async def generate_one(key, text, output, semaphore):
    if output.exists() and output.stat().st_size > 500:
        return True, key, None
    speech = SPEECH_OVERRIDES.get(key, spoken_text(text))
    if not speech:
        return True, key, None
    async with semaphore:
        for attempt in range(4):
            try:
                await edge_tts.Communicate(speech, VOICE, rate="-4%").save(str(output))
                if output.exists() and output.stat().st_size > 500:
                    return True, key, None
            except Exception as exc:
                error = str(exc)
            await asyncio.sleep(1.5 * (attempt + 1))
    return False, key, error


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--repair-zero", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--page-from", type=int)
    parser.add_argument("--page-to", type=int)
    parser.add_argument("--numbers-only", action="store_true")
    parser.add_argument("--adjacent-numbers-only", action="store_true")
    parser.add_argument("--length-units-only", action="store_true")
    parser.add_argument("--fractions-only", action="store_true")
    parser.add_argument("--cache-version")
    parser.add_argument("--version-only", action="store_true")
    parser.add_argument("--cleanup-temp", action="store_true")
    parser.add_argument("--keys-file")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    i18n = root / "content" / "i18n" / "sw-TZ"
    if args.cleanup_temp:
        old_temp = i18n / "audio_rehema_tmp"
        for attempt in range(10):
            locked = []
            for path in old_temp.glob("*"):
                if not path.is_file():
                    continue
                try:
                    path.unlink()
                except PermissionError:
                    locked.append(path)
            if not locked:
                break
            await asyncio.sleep(.5)
        if old_temp.exists():
            try:
                old_temp.rmdir()
            except PermissionError:
                pass
        print("Removed temporary audio generation files.")
        return
    texts = json.loads((i18n / "texts.json").read_text(encoding="utf-8"))
    audios_path = i18n / "audios.json"
    all_mappings = json.loads(audios_path.read_text(encoding="utf-8"))
    mappings = dict(all_mappings)
    if args.keys_file:
        selected = {line.strip() for line in Path(args.keys_file).read_text(encoding="utf-8").splitlines() if line.strip()}
        mappings = {key: name for key, name in mappings.items() if key in selected}
    target = i18n / "audio"
    if args.numbers_only:
        mappings = {key: name for key, name in mappings.items()
                    if re.search(r"\d", str(texts.get(key, "")))}
    if args.adjacent_numbers_only:
        mappings = {key: name for key, name in mappings.items()
                    if re.search(r"(?:[A-Za-z]\d|\d[A-Za-z]|\[\[blank:item-\d+\]\])",
                                 str(texts.get(key, "")))}
    if args.length_units_only:
        mappings = {
            key: name for key, name in mappings.items()
            if re.search(r"\b(?:km|hm|m)\b", str(texts.get(key, "")), flags=re.I)
        }
    if args.fractions_only:
        mappings = {
            key: name for key, name in mappings.items()
            if "<mfrac" in str(texts.get(key, ""))
        }
    if args.version_only:
        if not args.cache_version:
            raise SystemExit("--version-only requires --cache-version")
        for key, mapped_name in mappings.items():
            all_mappings[key] = f"{physical_audio_name(mapped_name)}?v={args.cache_version}"
        audios_path.write_text(json.dumps(all_mappings, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        print(f"Versioned {len(mappings)} audio mappings with {args.cache_version}.")
        return
    if args.page_from is not None or args.page_to is not None:
        first = args.page_from or 1
        last = args.page_to or 999
        mappings = {key: name for key, name in mappings.items()
                    if (match := re.match(r"pg(\d{3})_", key)) and first <= int(match.group(1)) <= last}
    if args.repair_zero:
        mappings = {key: name for key, name in mappings.items()
                    if not (target / physical_audio_name(name)).exists()
                    or (target / physical_audio_name(name)).stat().st_size <= 500}
    temp = i18n / ("audio_repair_tmp" if args.repair_zero else "audio_rehema_tmp")
    temp.mkdir(exist_ok=True)
    if args.force:
        for filename in mappings.values():
            output = temp / physical_audio_name(filename)
            if output.exists():
                output.unlink()
    semaphore = asyncio.Semaphore(args.workers)
    jobs = [generate_one(key, texts.get(key, ""), temp / physical_audio_name(filename), semaphore)
            for key, filename in mappings.items()]
    failures = []
    done = 0
    for future in asyncio.as_completed(jobs):
        ok, key, error = await future
        done += 1
        if not ok:
            failures.append((key, error))
        if done % 250 == 0:
            print(f"generated {done}/{len(jobs)}; failures={len(failures)}", flush=True)
    if failures:
        (temp / "failures.json").write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit(f"Audio generation incomplete: {len(failures)} failures")
    for filename in mappings.values():
        physical_name = physical_audio_name(filename)
        source = temp / physical_name
        if source.exists():
            for attempt in range(8):
                try:
                    shutil.copy2(source, target / physical_name)
                    break
                except PermissionError:
                    if attempt == 7:
                        raise
                    time.sleep(.4)
            source.unlink()
    try:
        temp.rmdir()
    except PermissionError:
        pass
    if args.cache_version:
        for key, mapped_name in mappings.items():
            all_mappings[key] = f"{physical_audio_name(mapped_name)}?v={args.cache_version}"
        audios_path.write_text(json.dumps(all_mappings, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(f"Replaced {len(mappings)} audio files with {VOICE}.")


if __name__ == "__main__":
    asyncio.run(main())
