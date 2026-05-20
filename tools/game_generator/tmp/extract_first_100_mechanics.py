#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET


XLSX_PATH = Path("/Users/hassan/Downloads/game_mechanic_tags_2026-2.xlsx")
OUT_PATH = Path(__file__).resolve().parent / "first_100_mechanics_rows.json"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def load_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    output: list[str] = []
    for item in root.findall("a:si", NS):
        text = "".join(node.text or "" for node in item.findall(".//a:t", NS))
        output.append(text)
    return output


def resolve_first_sheet_path(archive: ZipFile) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    first_sheet = workbook.find("a:sheets/a:sheet", NS)
    if first_sheet is None:
        raise SystemExit("No worksheets found in workbook")
    rel_id = first_sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
    if not rel_id:
        raise SystemExit("First worksheet missing relationship id")
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    for rel in rels.findall("rel:Relationship", NS):
        if rel.attrib.get("Id") == rel_id:
            target = rel.attrib.get("Target")
            if not target:
                break
            return f"xl/{target}"
    raise SystemExit(f"Could not resolve worksheet target for relationship id {rel_id}")


def cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("a:v", NS)
    if value_node is None or value_node.text is None:
        return ""
    raw_value = value_node.text
    if cell_type == "s":
        return shared_strings[int(raw_value)]
    return raw_value


def extract_rows(sheet_xml: str, shared_strings: list[str]) -> list[dict[str, object]]:
    root = ET.fromstring(sheet_xml)
    rows = root.findall(".//a:sheetData/a:row", NS)
    extracted: list[dict[str, object]] = []
    for row in rows[2:102]:
        values = [cell_value(cell, shared_strings) for cell in row.findall("a:c", NS)]
        if len(values) < 10:
            values.extend([""] * (10 - len(values)))
        rank = values[0].strip()
        mechanic = values[1].strip()
        if not rank or not mechanic:
            continue
        try:
            rank_value = int(float(rank))
        except ValueError as exc:
            raise SystemExit(f"Could not parse rank value '{rank}'") from exc

        extracted.append(
            {
                "rank": rank_value,
                "mechanic": mechanic,
                "feel": [value.strip() for value in values[2:5] if value.strip()],
                "hashtags": [value.strip() for value in values[5].split(",") if value.strip()],
                "player_context": values[6].strip(),
                "game_tags": [value.strip() for value in values[7].split(",") if value.strip()],
                "aesthetic_tags": [value.strip() for value in values[8].split(",") if value.strip()],
                "meme_tags": [value.strip() for value in values[9].split(",") if value.strip()],
            }
        )
    return extracted


def main() -> int:
    if not XLSX_PATH.is_file():
        raise SystemExit(f"Missing xlsx: {XLSX_PATH}")

    with ZipFile(XLSX_PATH) as archive:
        shared_strings = load_shared_strings(archive)
        sheet_path = resolve_first_sheet_path(archive)
        rows = extract_rows(archive.read(sheet_path).decode("utf-8"), shared_strings)

    payload = {
        "source_xlsx": str(XLSX_PATH),
        "row_count": len(rows),
        "rows": rows,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"out_path": str(OUT_PATH), "row_count": len(rows), "sample_mechanics": [row["mechanic"] for row in rows[:10]]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())