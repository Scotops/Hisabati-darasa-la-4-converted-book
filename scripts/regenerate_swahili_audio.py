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
    text = re.sub(
        r"<mfrac[^>]*>\s*<mn[^>]*>1</mn>\s*<mn[^>]*>2</mn>\s*</mfrac>",
        " nusu ",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r"<mfrac[^>]*>\s*<mn[^>]*>1</mn>\s*<mn[^>]*>(\d+)</mn>\s*</mfrac>",
        r" moja ya \1 ",
        text,
        flags=re.I | re.S,
    )
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
        text = fraction.sub(r" \1 juu ya \2 ", text)
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
        (r"\bmL\b", "mililita"), (r"\bkm\b", "kilometa"),
        (r"\bsm\b", "sentimeta"), (r"\bmm\b", "milimeta"),
        (r"\bkg\b", "kilogramu"), (r"\bhg\b", "hektogramu"),
        (r"\bg\b", "gramu"), (r"\bL\b", "lita"),
        (r"\bsh\b", "shilingi"), (r"\bst\b", "senti"),
        (r"\bm\b", "meta"),
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
    speech = spoken_text(text)
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
