from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any

from flask import Blueprint, Response, current_app, render_template, request

from ..email.send import send_report
from ..parser.foxwell import parse_foxwell_output
from ..parser.interpret import interpret_codes
from ..report.generator import ReportContext, VehicleInfo, generate_report
from ..storage import models
from ..utils.files import is_allowed_image, save_upload
from ..utils.i18n import available_languages, translate
from .auth import requires_auth

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET", "POST"])
@requires_auth
def upload() -> Response | str:
    settings = current_app.config["SETTINGS"]
    language = request.form.get("language", "en")
    language_options = sorted(set(available_languages())) or ["en"]
    if language not in language_options:
        language = "en"

    localize = partial(translate, language=language)
    errors: list[str] = []
    summary: dict[str, Any] | None = None

    if request.method == "POST":
        scanner_file = request.files.get("scanner_file")
        images = request.files.getlist("images")
        recipient = request.form.get("email", "").strip()
        vin = request.form.get("vin", "").strip() or None
        mileage = request.form.get("mileage", "").strip() or None
        notes = request.form.get("notes", "").strip() or None

        if not scanner_file or not scanner_file.filename:
            errors.append(localize("upload.errors.missing_scanner", default="Scanner file is required."))
        if not recipient:
            errors.append(localize("upload.errors.missing_email", default="Email address is required."))

        image_paths: list[Path] = []
        if not errors:
            invalid_images = [img.filename for img in images if img and img.filename and not is_allowed_image(img.filename)]
            if invalid_images:
                errors.append(
                    localize(
                        "upload.errors.invalid_images",
                        default="Only JPG images are supported.",
                        filenames=", ".join(filter(None, invalid_images)),
                    )
                )

        if errors:
            return render_template(
                "upload.html",
                language=language,
                languages=language_options,
                errors=errors,
                summary=summary,
                translate=localize,
            )

        report_id = uuid.uuid4().hex
        created_at = datetime.now(timezone.utc)
        scanner_path = save_upload(scanner_file, settings.upload_dir, f"{report_id}_scanner")

        for index, image in enumerate(images):
            if image and image.filename:
                image_paths.append(save_upload(image, settings.upload_dir, f"{report_id}_image{index}"))

        try:
            raw_entries = parse_foxwell_output(scanner_path)
        except Exception as exc:  # pragma: no cover - defensive against malformed files
            errors.append(
                localize(
                    "upload.errors.parse_failed",
                    default="Unable to parse scanner file: {error}",
                    error=str(exc),
                )
            )
            scanner_path.unlink(missing_ok=True)
            for path in image_paths:
                path.unlink(missing_ok=True)
            return render_template(
                "upload.html",
                language=language,
                languages=language_options,
                errors=errors,
                summary=summary,
                translate=localize,
            )

        interpreted = interpret_codes(raw_entries, language)

        report_context = ReportContext(
            report_id=report_id,
            created_at=created_at,
            language=language,
            vehicle=VehicleInfo(vin=vin, mileage=mileage, notes=notes),
            codes=interpreted,
            images=image_paths,
        )
        pdf_path = generate_report(report_context, settings)

        subject = localize(
            "email.subject",
            default="Vehicle diagnostic report for {vin}",
            vin=vin or report_id,
        )
        body = localize(
            "email.body",
            default=(
                "Attached is the diagnostic report for your vehicle. \n\n"
                "Report ID: {report_id}\nDetected codes: {codes}"
            ),
            report_id=report_id,
            codes=", ".join(code.code for code in interpreted) or localize(
                "report.diagnostics.no_codes",
                default="None",
            ),
        )
        email_sent = send_report(recipient, subject, body, pdf_path, settings)

        metadata = {
            "created_at": created_at,
            "scanner_file": str(scanner_path),
            "image_paths": [str(path) for path in image_paths],
            "pdf_path": str(pdf_path),
            "email": recipient,
            "language": language,
            "vehicle": asdict(report_context.vehicle),
            "codes": [asdict(code) for code in interpreted],
        }
        models.store_report(settings, report_id, metadata)

        summary = {
            "report_id": report_id,
            "created_at": created_at,
            "email_sent": email_sent,
            "pdf_path": pdf_path,
            "codes": interpreted,
            "vehicle": report_context.vehicle,
            "email": recipient,
        }

    return render_template(
        "upload.html",
        language=language,
        languages=language_options,
        errors=errors,
        summary=summary,
        translate=localize,
    )
