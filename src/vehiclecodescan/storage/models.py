from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List

from ..config import Settings

DB_FILENAME = "metadata.db"


@dataclass
class ReportRecord:
    report_id: str
    created_at: datetime
    metadata: dict[str, Any]


def _db_path(settings: Settings) -> Path:
    return settings.storage_root / DB_FILENAME


def _connect(settings: Settings) -> sqlite3.Connection:
    path = _db_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def init_db(settings: Settings) -> None:
    with _connect(settings) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )
        conn.commit()


def store_report(settings: Settings, report_id: str, metadata: dict[str, Any]) -> None:
    init_db(settings)
    created_at = metadata.get("created_at")
    if isinstance(created_at, datetime):
        created_at_str = created_at.astimezone(timezone.utc).isoformat()
        metadata = {**metadata, "created_at": created_at_str}
    elif isinstance(created_at, str):
        created_at_str = created_at
    else:
        created_at_str = datetime.now(timezone.utc).isoformat()
        metadata = {**metadata, "created_at": created_at_str}
    with _connect(settings) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO reports (report_id, created_at, metadata) VALUES (?, ?, ?)",
            (report_id, created_at_str, json.dumps(metadata)),
        )
        conn.commit()


def list_reports(settings: Settings) -> List[ReportRecord]:
    init_db(settings)
    with _connect(settings) as conn:
        rows = conn.execute("SELECT report_id, created_at, metadata FROM reports").fetchall()
    records: List[ReportRecord] = []
    for report_id, created_at, metadata_json in rows:
        metadata = json.loads(metadata_json)
        records.append(
            ReportRecord(
                report_id=report_id,
                created_at=datetime.fromisoformat(created_at).astimezone(timezone.utc),
                metadata=metadata,
            )
        )
    return records


def get_reports_older_than(settings: Settings, cutoff: datetime) -> List[ReportRecord]:
    init_db(settings)
    cutoff_iso = cutoff.astimezone(timezone.utc).isoformat()
    with _connect(settings) as conn:
        rows = conn.execute(
            "SELECT report_id, created_at, metadata FROM reports WHERE created_at < ?",
            (cutoff_iso,),
        ).fetchall()
    results: List[ReportRecord] = []
    for report_id, created_at, metadata_json in rows:
        results.append(
            ReportRecord(
                report_id=report_id,
                created_at=datetime.fromisoformat(created_at).astimezone(timezone.utc),
                metadata=json.loads(metadata_json),
            )
        )
    return results


def delete_reports(settings: Settings, report_ids: Iterable[str]) -> None:
    init_db(settings)
    with _connect(settings) as conn:
        conn.executemany("DELETE FROM reports WHERE report_id = ?", [(rid,) for rid in report_ids])
        conn.commit()
