from __future__ import annotations

import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from ..config import MailSettings, Settings


def send_report(recipient: str, subject: str, body: str, pdf_path: Path, settings: Settings) -> bool:
    mail_settings = settings.mail
    if mail_settings is None:
        print("Mail settings not configured; skipping email send.")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = mail_settings.sender
    message["To"] = recipient
    message.set_content(body)

    with pdf_path.open("rb") as handle:
        message.add_attachment(
            handle.read(),
            maintype="application",
            subtype="pdf",
            filename=pdf_path.name,
        )

    with _connect(mail_settings) as server:
        if mail_settings.use_tls:
            server.starttls()
        if mail_settings.username:
            server.login(mail_settings.username, mail_settings.password)
        server.send_message(message)
    return True


class _SMTPConnection:
    def __init__(self, settings: MailSettings):
        self.settings = settings
        self.server: smtplib.SMTP | None = None

    def __enter__(self) -> smtplib.SMTP:
        self.server = smtplib.SMTP(self.settings.server, self.settings.port, timeout=30)
        return self.server

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.server is not None:
            try:
                self.server.quit()
            except smtplib.SMTPException:
                self.server.close()


def _connect(settings: MailSettings) -> _SMTPConnection:
    return _SMTPConnection(settings)
