from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..config import Settings
from ..parser.interpret import InterpretedCode
from ..utils.i18n import translate


@dataclass
class VehicleInfo:
    vin: str | None = None
    mileage: str | None = None
    notes: str | None = None


@dataclass
class ReportContext:
    report_id: str
    created_at: datetime
    language: str
    vehicle: VehicleInfo
    codes: Sequence[InterpretedCode]
    images: Sequence[Path]


def generate_report(context: ReportContext, settings: Settings) -> Path:
    pdf_path = settings.report_dir / f"{context.report_id}.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    heading = styles["Heading1"]
    subheading = styles["Heading2"]
    normal = styles["BodyText"]
    normal.spaceAfter = 12
    disclaimer_style = ParagraphStyle(
        name="Disclaimer",
        parent=normal,
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#555555"),
    )

    lang = context.language
    story = []

    story.append(Paragraph(translate("report.title", lang, default="Vehicle Diagnostic Report"), heading))
    generated_on = context.created_at.strftime("%Y-%m-%d %H:%M %Z")
    story.append(
        Paragraph(
            translate("report.generated_on", lang, default="Generated on {timestamp}", timestamp=generated_on),
            normal,
        )
    )
    story.append(Spacer(1, 12))

    vehicle_rows = []
    if context.vehicle.vin:
        vehicle_rows.append([
            Paragraph(translate("report.vehicle.vin", lang, default="VIN"), normal),
            Paragraph(escape(context.vehicle.vin), normal),
        ])
    if context.vehicle.mileage:
        vehicle_rows.append([
            Paragraph(translate("report.vehicle.mileage", lang, default="Mileage"), normal),
            Paragraph(escape(context.vehicle.mileage), normal),
        ])
    if context.vehicle.notes:
        notes_text = escape(context.vehicle.notes).replace("\n", "<br/>")
        vehicle_rows.append([
            Paragraph(translate("report.vehicle.notes", lang, default="Notes"), normal),
            Paragraph(notes_text, normal),
        ])

    if vehicle_rows:
        story.append(Paragraph(translate("report.vehicle.heading", lang, default="Vehicle"), subheading))
        table = Table(vehicle_rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 12))

    story.append(Paragraph(translate("report.diagnostics.heading", lang, default="Diagnostics"), subheading))

    if context.codes:
        data = [
            [
                translate("report.diagnostics.code", lang, default="Code"),
                translate("report.diagnostics.status", lang, default="Status"),
                translate("report.diagnostics.severity", lang, default="Severity"),
                translate("report.diagnostics.description", lang, default="Description"),
                translate("report.diagnostics.recommendation", lang, default="Recommendation"),
            ]
        ]
        for code in context.codes:
            data.append([
                code.code,
                code.status or "-",
                code.severity_label,
                code.description,
                code.advice,
            ])
        table = Table(data, hAlign="LEFT", colWidths=[70, 70, 90, 180, 180])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
    else:
        story.append(
            Paragraph(
                translate("report.diagnostics.no_codes", lang, default="No diagnostic trouble codes were detected."),
                normal,
            )
        )
    story.append(Spacer(1, 12))

    if context.images:
        story.append(Paragraph(translate("report.images.heading", lang, default="Images"), subheading))
        for image_path in context.images:
            img = Image(str(image_path))
            max_width = 6.5 * inch
            if img.drawWidth > max_width:
                scale = max_width / img.drawWidth
                img.drawWidth *= scale
                img.drawHeight *= scale
            story.append(img)
            story.append(Spacer(1, 6))

    disclaimer_title = translate("report.disclaimer.title", lang, default="Disclaimer")
    disclaimer_text = translate(
        "report.disclaimer.body",
        lang,
        default=(
            "This report is provided for informational purposes only. Seek assistance from a certified technician for any "
            "required repairs."
        ),
    )
    story.append(Spacer(1, 12))
    story.append(Paragraph(disclaimer_title, subheading))
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    return pdf_path
