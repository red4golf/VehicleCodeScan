from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

from ..utils.i18n import translate
from .foxwell import RawDiagnosticEntry

_MODULE_PATH = Path(__file__).resolve()
_DATA_SEARCH = [
    _MODULE_PATH.parents[2] / "data" / "obd_codes.json",
    Path.cwd() / "data" / "obd_codes.json",
]
for _candidate in _DATA_SEARCH:
    if _candidate.exists():
        DATA_PATH = _candidate
        break
else:  # pragma: no cover - fallback for unusual setups
    DATA_PATH = _MODULE_PATH.parent / "obd_codes.json"


@dataclass
class InterpretedCode:
    code: str
    description: str
    severity: str
    severity_label: str
    advice: str
    status: str | None
    known: bool


@lru_cache(maxsize=1)
def _load_database() -> dict[str, dict]:
    if not DATA_PATH.exists():
        return {}
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def interpret_codes(entries: Iterable[RawDiagnosticEntry], language: str) -> List[InterpretedCode]:
    database = _load_database()
    results: List[InterpretedCode] = []
    for entry in entries:
        record = database.get(entry.code.upper())
        if record:
            description = _get_localized(record.get("description", {}), language)
            advice = _get_localized(record.get("advice", {}), language)
            severity = record.get("severity", "unknown")
            severity_label = translate(f"severity.{severity}", language, default=severity.title())
            results.append(
                InterpretedCode(
                    code=entry.code.upper(),
                    description=description,
                    severity=severity,
                    severity_label=severity_label,
                    advice=advice,
                    status=entry.status,
                    known=True,
                )
            )
        else:
            default_description = translate(
                "report.unknown_code_description",
                language,
                default="No database entry for code {code}.",
                code=entry.code.upper(),
            )
            default_advice = translate(
                "report.unknown_code_advice",
                language,
                default="Refer to a qualified technician for further diagnosis.",
            )
            severity_label = translate("severity.unknown", language, default="Unknown")
            results.append(
                InterpretedCode(
                    code=entry.code.upper(),
                    description=default_description,
                    severity="unknown",
                    severity_label=severity_label,
                    advice=default_advice,
                    status=entry.status,
                    known=False,
                )
            )
    return results


def _get_localized(field: dict, language: str) -> str:
    if isinstance(field, dict):
        if language in field:
            return field[language]
        if "en" in field:
            return field["en"]
    return str(field)
