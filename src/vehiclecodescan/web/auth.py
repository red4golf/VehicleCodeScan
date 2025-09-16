from __future__ import annotations

import secrets
from functools import wraps
from typing import Callable, TypeVar, cast

from flask import Response, current_app, request

F = TypeVar("F", bound=Callable[..., Response])


def _check_auth(username: str, password: str) -> bool:
    settings = current_app.config["SETTINGS"]
    return secrets.compare_digest(username, settings.admin_username) and secrets.compare_digest(
        password, settings.admin_password
    )


def _authenticate() -> Response:
    return Response("Authentication required", 401, {"WWW-Authenticate": 'Basic realm="Login Required"'})


def requires_auth(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[override]
        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return _authenticate()
        return func(*args, **kwargs)

    return cast(F, wrapper)
