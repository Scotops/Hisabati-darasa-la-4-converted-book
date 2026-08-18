"""Merge split ADT sections into one reader entry per source-PDF page.

The source book has 184 physical pages.  The original ADT spine expanded
multi-section pages into separate reader entries and omitted blank PDF page 6.
This migration keeps every content/audio ID and interactive activity while
restoring a one-to-one physical-page spine.
"""

from __future__ import annotations

import copy
import json
import re
from collections import defaultdict
from pathlib import Path

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
PAGES_PATH = ROOT / "content" / "pages.json"
TOC_PATH = ROOT / "content" / "toc.json"
PURE_ANSWERS = re.compile(
    r"^\s*window\.correctAnswers\s*=\s*(\{.*\})\s*;?\s*$", re.DOTALL
)
PAGE_ID = re.compile(r"^(pg\d{3})_sec\d{3}$")


def load_tree(path: Path):
    parser = html.HTMLParser(encoding="utf-8", remove_comments=False)
    return html.parse(str(path), parser=parser)


def page_prefix(section_id: str) -> str:
    match = PAGE_ID.match(section_id)
    if not match:
        raise ValueError(f"Unexpected section ID: {section_id}")
    return match.group(1)


def source_path(entry: dict) -> Path:
    return ROOT / entry["href"]


def clean_content_class(value: str | None) -> str:
    classes = (value or "").split()
    return " ".join(c for c in classes if c not in {"opacity-0", "opacity-100"})


def element_by_id(tree, element_id: str):
    matches = tree.xpath(f'.//*[@id="{element_id}"]')
    if not matches:
        raise KeyError(element_id)
    return matches[0]


def namespace_activity_items(raw: str, section_id: str) -> str:
    """Avoid item-1 collisions when two activities share a physical page."""
    return re.sub(r"(?<![\w-])item-(\d+)(?![\w-])", rf"{section_id}-item-\1", raw)


def load_source(entry: dict, namespace: bool):
    raw = source_path(entry).read_text(encoding="utf-8")
    if namespace:
        raw = namespace_activity_items(raw, entry["section_id"])
    parser = html.HTMLParser(encoding="utf-8", remove_comments=False)
    return html.document_fromstring(raw, parser=parser).getroottree()


def replace_old_section_refs(value):
    if isinstance(value, str):
        return re.sub(r"(pg\d{3})_sec\d{3}", r"\1_sec001", value)
    if isinstance(value, list):
        return [replace_old_section_refs(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_old_section_refs(item) for key, item in value.items()}
    return value


def build_blank_page(page_index: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="sw-TZ">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="title-id" content="pg006_sec001">
  <meta name="page-section-id" content="{page_index}">
  <link href="./content/tailwind_output.css" rel="stylesheet">
  <link href="./assets/libs/fontawesome/css/all.min.css" rel="stylesheet">
  <link href="./assets/fonts.css" rel="stylesheet">
</head>
<body>
  <main id="main-content" class="min-h-screen">
    <div id="content" class="opacity-0">
      <section role="article" data-section-type="blank" data-section-id="pg006_sec001" aria-hidden="true"></section>
    </div>
  </main>
  <div id="interface-container"></div>
  <div id="nav-container"></div>
  <script src="./assets/offline-preloader.js"></script>
  <script src="./assets/scorm.js"></script>
  <script src="./assets/book-quality.js"></script>
  <script src="./assets/base.bundle.local.js?v=20260818" type="module"></script>
</body>
</html>
"""


def merge_page(page_number: int, entries: list[dict], spine_index: int) -> None:
    canonical_path = ROOT / ("index.html" if page_number == 1 else f"pg{page_number:03d}_sec001.html")
    if not entries:
        if page_number != 6:
            raise ValueError(f"No source sections for page {page_number}")
        canonical_path.write_text(build_blank_page(spine_index), encoding="utf-8")
        return

    # Only pages containing more than one activity need item-key namespacing.
    activity_sections = []
    for entry in entries:
        raw = source_path(entry).read_text(encoding="utf-8")
        if "data-activity-item" in raw or "window.correctAnswers" in raw:
            activity_sections.append(entry["section_id"])
    namespace = len(activity_sections) > 1

    trees = [load_source(entry, namespace) for entry in entries]
    target = trees[0]
    root = target.getroot()
    body = root.find("body")
    head = root.find("head")
    content = element_by_id(target, "content")

    # Preserve the top-level reader fade behavior, but isolate each original
    # section's layout classes inside its own wrapper.
    for child in list(content):
        content.remove(child)
    content.set("class", "opacity-0")

    answer_maps: dict[str, object] = {}
    extra_inline_scripts = []
    seen_styles = {etree.tostring(s, encoding="unicode") for s in head.findall("style")}

    for source_index, (entry, tree) in enumerate(zip(entries, trees)):
        source_content = element_by_id(tree, "content")
        wrapper = etree.Element("div")
        wrapper.set("data-source-section", entry["section_id"])
        wrapper_class = clean_content_class(source_content.get("class"))
        wrapper.set("class", f"adt-physical-page-part {wrapper_class}".strip())
        for child in source_content:
            wrapper.append(copy.deepcopy(child))
        content.append(wrapper)

        source_head = tree.getroot().find("head")
        for style in source_head.findall("style"):
            rendered = etree.tostring(style, encoding="unicode")
            if rendered not in seen_styles:
                head.append(copy.deepcopy(style))
                seen_styles.add(rendered)

        source_body = tree.getroot().find("body")
        for script in source_body.findall("script"):
            if script.get("src"):
                continue
            script_text = script.text or ""
            match = PURE_ANSWERS.match(script_text)
            if match:
                data = json.loads(match.group(1))
                overlap = set(answer_maps).intersection(data)
                if overlap:
                    raise ValueError(
                        f"Duplicate activity keys on page {page_number}: {sorted(overlap)}"
                    )
                answer_maps.update(data)
                if source_index == 0:
                    parent = script.getparent()
                    if parent is not None:
                        parent.remove(script)
            elif source_index > 0 and script_text.strip():
                extra_inline_scripts.append(copy.deepcopy(script))

    # Insert merged activity data and secondary inline behavior before the UI.
    interface = None
    try:
        interface = element_by_id(target, "interface-container")
    except KeyError:
        pass
    insertion_index = body.index(interface) if interface is not None else len(body)
    if answer_maps:
        script = etree.Element("script")
        script.text = "window.correctAnswers = " + json.dumps(
            answer_maps, ensure_ascii=False, separators=(",", ":")
        ) + ";"
        body.insert(insertion_index, script)
        insertion_index += 1
    for script in extra_inline_scripts:
        body.insert(insertion_index, script)
        insertion_index += 1

    title_meta = head.xpath('.//meta[@name="title-id"]')
    section_meta = head.xpath('.//meta[@name="page-section-id"]')
    if title_meta:
        title_meta[0].set("content", f"pg{page_number:03d}_sec001")
    if section_meta:
        section_meta[0].set("content", str(spine_index))

    rendered = etree.tostring(
        root,
        method="html",
        encoding="unicode",
        doctype="<!DOCTYPE html>",
        pretty_print=False,
    )
    canonical_path.write_text(rendered, encoding="utf-8")


def main() -> None:
    old_pages = json.loads(PAGES_PATH.read_text(encoding="utf-8"))
    if len(old_pages) != 277:
        raise RuntimeError(
            "This one-time migration expects the original 277-entry manifest. "
            "The book appears to have already been compressed."
        )
    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in old_pages:
        grouped[page_prefix(entry["section_id"])].append(entry)

    new_pages = []
    for page_number in range(1, 185):
        prefix = f"pg{page_number:03d}"
        entries = grouped.get(prefix, [])
        merge_page(page_number, entries, page_number)
        entry = {
            "section_id": f"{prefix}_sec001",
            "href": "index.html" if page_number == 1 else f"{prefix}_sec001.html",
            "page_number": page_number,
        }
        new_pages.append(entry)

    PAGES_PATH.write_text(
        json.dumps(new_pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    toc = json.loads(TOC_PATH.read_text(encoding="utf-8"))
    TOC_PATH.write_text(
        json.dumps(replace_old_section_refs(toc), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Compressed {len(old_pages)} reader entries to {len(new_pages)} physical pages.")


if __name__ == "__main__":
    main()
