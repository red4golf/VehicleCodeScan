from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

CODE_PATTERN = re.compile(r"\b([PCBU][0-9A-F]{4})\b", re.IGNORECASE)
STATUS_KEYWORDS = {
    "pending": "pending",
    "stored": "stored",
    "history": "history",
    "permanent": "permanent",
    "active": "active",
}


@dataclass
class RawDiagnosticEntry:
    code: str
    status: str | None = None
    source: str | None = None


def parse_foxwell_output(path: Path) -> List[RawDiagnosticEntry]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _parse_csv(path)
    return _parse_text(path)


def _parse_csv(path: Path) -> List[RawDiagnosticEntry]:
    entries: List[RawDiagnosticEntry] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        code_field = _find_code_field(reader.fieldnames or [])
        for row in reader:
            code = _normalize_code(row.get(code_field, "")) if code_field else None
            if not code:
                code = _find_code_in_row(row.values())
            if not code:
                continue
            status = _find_status(row.values())
            entries.append(RawDiagnosticEntry(code=code, status=status, source="csv"))
    if entries:
        return entries
    # fallback to text parsing if CSV headers unknown
    return _parse_text(path)


def _find_code_field(headers: Iterable[str]) -> str | None:
    header_pairs = [((header or "").strip(), (header or "").strip().lower()) for header in headers]
    for original, lowered in header_pairs:
        if any(keyword in lowered for keyword in ("code", "dtc", "fault")):
            return original
    return None


def _find_code_in_row(values: Iterable[str]) -> str | None:
    for value in values:
        if not value:
            continue
        match = CODE_PATTERN.search(value)
        if match:
            return match.group(1).upper()
    return None


def _find_status(values: Iterable[str]) -> str | None:
    for value in values:
        if not value:
            continue
        lower_value = value.lower()
        for keyword, label in STATUS_KEYWORDS.items():
            if keyword in lower_value:
                return label
    return None


def _normalize_code(value: str | None) -> str | None:
    if not value:
        return None
    match = CODE_PATTERN.search(value)
    if not match:
        return None
    return match.group(1).upper()


def _parse_text(path: Path) -> List[RawDiagnosticEntry]:
    entries: List[RawDiagnosticEntry] = []
    with path.open("r", encoding="utf-8-sig", errors="ignore") as handle:
        for line in handle:
            matches = CODE_PATTERN.findall(line)
            if not matches:
                continue
            status = _find_status([line])
            for code in matches:
                entries.append(RawDiagnosticEntry(code=code.upper(), status=status, source="text"))
    return entries
