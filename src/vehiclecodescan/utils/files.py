from __future__ import annotations

import mimetypes
import os
import uuid
from pathlib import Path
from typing import Iterable

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg"}


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_allowed_image(filename: str) -> bool:
    extension = Path(filename).suffix.lower()
    return extension in ALLOWED_IMAGE_EXTENSIONS


def is_probably_text(path: Path) -> bool:
    mime, _ = mimetypes.guess_type(path.name)
    return mime in {"text/plain", "text/csv", "application/csv"}


def save_upload(file: FileStorage, destination: Path, prefix: str | None = None) -> Path:
    ensure_directory(destination)
    original = secure_filename(file.filename or "upload")
    extension = Path(original).suffix or ".bin"
    name_prefix = prefix or uuid.uuid4().hex
    filename = f"{name_prefix}{extension}"
    target = destination / filename
    file.save(target)
    return target


def remove_files(paths: Iterable[os.PathLike[str] | str]) -> None:
    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            continue
