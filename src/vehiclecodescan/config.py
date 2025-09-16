from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class MailSettings:
    server: str
    port: int
    username: str
    password: str
    sender: str
    use_tls: bool = True


@dataclass
class Settings:
    secret_key: str
    storage_root: Path
    upload_dir: Path
    report_dir: Path
    mail: Optional[MailSettings]
    admin_username: str
    admin_password: str


def get_settings() -> Settings:
    base_dir = Path(os.environ.get("APP_STORAGE_ROOT", "storage"))
    upload_dir = base_dir / "uploads"
    report_dir = base_dir / "reports"
    upload_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    secret_key = os.environ.get("APP_SECRET_KEY", "development-secret")
    admin_username = os.environ.get("APP_USERNAME", "admin")
    admin_password = os.environ.get("APP_PASSWORD", "password")

    if "MAIL_SERVER" in os.environ:
        mail = MailSettings(
            server=os.environ["MAIL_SERVER"],
            port=int(os.environ.get("MAIL_PORT", "587")),
            username=os.environ.get("MAIL_USERNAME", ""),
            password=os.environ.get("MAIL_PASSWORD", ""),
            sender=os.environ.get("MAIL_SENDER", "reports@example.com"),
            use_tls=os.environ.get("MAIL_USE_TLS", "true").lower() == "true",
        )
    else:
        mail = None

    return Settings(
        secret_key=secret_key,
        storage_root=base_dir,
        upload_dir=upload_dir,
        report_dir=report_dir,
        mail=mail,
        admin_username=admin_username,
        admin_password=admin_password,
    )
