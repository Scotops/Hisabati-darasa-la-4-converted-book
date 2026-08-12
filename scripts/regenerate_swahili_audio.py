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
    if value == 1000:
        return "elfu moja"
    return str(value)


def roman_spoken(token):
    return f"{swahili_number(int(roman_value(token)))} ya Kirumi"


def spoken_text(value):
    text = html.unescape(str(value))
    fraction = re.compile(r"<mfrac[^>]*>\s*<[^>]+>(.*?)</[^>]+>\s*<[^>]+>(.*?)</[^>]+>\s*</mfrac>", re.I | re.S)
    while fraction.search(text):
        text = fraction.sub(r" \1 juu ya \2 ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b[IVXLCDM]+\b", lambda match: roman_spoken(match.group(0)), text)
    substitutions = {
        "×": " mara ", "÷": " gawanya kwa ", "−": " kutoa ",
        "=": " ni sawa na ", "<": " ni ndogo kuliko ", ">": " ni kubwa kuliko ",
        "+": " jumlisha ",
    }
    for symbol, words in substitutions.items():
        text = text.replace(symbol, words)
    text = re.sub(r"\[\[blank:item-\d+\]\]", " nafasi ya jibu ", text)
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
    parser.add_argument("--cleanup-temp", action="store_true")
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
    mappings = json.loads((i18n / "audios.json").read_text(encoding="utf-8"))
    target = i18n / "audio"
    if args.page_from is not None or args.page_to is not None:
        first = args.page_from or 1
        last = args.page_to or 999
        mappings = {key: name for key, name in mappings.items()
                    if (match := re.match(r"pg(\d{3})_", key)) and first <= int(match.group(1)) <= last}
    if args.repair_zero:
        mappings = {key: name for key, name in mappings.items()
                    if not (target / name).exists() or (target / name).stat().st_size <= 500}
    temp = i18n / ("audio_repair_tmp" if args.repair_zero else "audio_rehema_tmp")
    temp.mkdir(exist_ok=True)
    if args.force:
        for filename in mappings.values():
            output = temp / filename
            if output.exists():
                output.unlink()
    semaphore = asyncio.Semaphore(args.workers)
    jobs = [generate_one(key, texts.get(key, ""), temp / filename, semaphore)
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
        source = temp / filename
        if source.exists():
            for attempt in range(8):
                try:
                    shutil.copy2(source, target / filename)
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
    print(f"Replaced {len(mappings)} audio files with {VOICE}.")


if __name__ == "__main__":
    asyncio.run(main())
