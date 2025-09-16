"""Generate a sample vehicle diagnostic PDF report for demo purposes."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vehiclecodescan.config import Settings
from vehiclecodescan.parser.foxwell import RawDiagnosticEntry
from vehiclecodescan.parser.interpret import interpret_codes
from vehiclecodescan.report.generator import ReportContext, VehicleInfo, generate_report


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    upload_dir = base_dir / "_uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        secret_key="demo",
        storage_root=base_dir,
        upload_dir=upload_dir,
        report_dir=base_dir,
        mail=None,
        admin_username="demo",
        admin_password="demo",
    )

    sample_entries = [
        RawDiagnosticEntry(code="P0300", status="stored"),
        RawDiagnosticEntry(code="P0420", status="pending"),
        RawDiagnosticEntry(code="P0442", status="history"),
        RawDiagnosticEntry(code="P0171", status="active"),
    ]

    interpreted_codes = interpret_codes(sample_entries, language="en")

    context = ReportContext(
        report_id="sample-report",
        created_at=datetime.now(timezone.utc),
        language="en",
        vehicle=VehicleInfo(
            vin="1HGCM82633A123456",
            mileage="123,456 miles",
            notes="Customer reports occasional rough idle.\nNo prior repairs recorded.",
        ),
        codes=interpreted_codes,
        images=[],
    )

    pdf_path = generate_report(context, settings)
    print(f"Sample report created at {pdf_path}")


if __name__ == "__main__":
    main()
