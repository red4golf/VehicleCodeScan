from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# Attempt to locate the project root where the i18n directory lives. This allows
# the module to function both when run from the repository as well as when the
# package is installed in site-packages and the assets are mounted in the working
# directory (e.g., inside the Docker container).
_MODULE_PATH = Path(__file__).resolve()
_SEARCH_PATHS = [
    _MODULE_PATH.parents[2],
    Path.cwd(),
]
for _base in _SEARCH_PATHS:
    candidate = (_base / "i18n").resolve()
    if candidate.exists():
        I18N_DIR = candidate
        break
else:  # pragma: no cover - fallback for unusual setups
    I18N_DIR = (_MODULE_PATH.parent / "i18n").resolve()
DEFAULT_LANGUAGE = "en"


@lru_cache(maxsize=None)
def _load_language(language: str) -> dict[str, Any]:
    path = I18N_DIR / f"{language}.json"
    if not path.exists():
        if language == DEFAULT_LANGUAGE:
            return {}
        return _load_language(DEFAULT_LANGUAGE)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _lookup(data: dict[str, Any], key: str) -> Any:
    current: Any = data
    for part in key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def translate(key: str, language: str, default: str | None = None, **kwargs: Any) -> str:
    value = _lookup(_load_language(language), key)
    if value is None and language != DEFAULT_LANGUAGE:
        value = _lookup(_load_language(DEFAULT_LANGUAGE), key)
    if value is None:
        value = default if default is not None else key
    if isinstance(value, str):
        return value.format(**kwargs)
    return str(value)


def available_languages() -> list[str]:
    return [path.stem for path in I18N_DIR.glob("*.json")]
