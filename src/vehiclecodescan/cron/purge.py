from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..config import get_settings
from ..storage import models
from ..utils.files import remove_files


def purge_expired(days: int = 30) -> None:
    settings = get_settings()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    expired = models.get_reports_older_than(settings, cutoff)
    if not expired:
        print("No expired reports to purge.")
        return
    to_delete_ids = []
    for record in expired:
        metadata = record.metadata
        paths: list[Path] = []
        scanner_path = metadata.get("scanner_file")
        if scanner_path:
            paths.append(Path(scanner_path))
        pdf_path = metadata.get("pdf_path")
        if pdf_path:
            paths.append(Path(pdf_path))
        for image_path in metadata.get("image_paths", []):
            paths.append(Path(image_path))
        remove_files(paths)
        to_delete_ids.append(record.report_id)
    models.delete_reports(settings, to_delete_ids)
    print(f"Purged {len(to_delete_ids)} reports older than {days} days.")


if __name__ == "__main__":
    purge_expired()
