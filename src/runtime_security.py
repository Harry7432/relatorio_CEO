import os
import re
from collections.abc import Iterable
from enum import Enum
from typing import Any


REDACTED = "[REDACTED]"


class OperationalErrorCategory(str, Enum):
    CONFIGURATION = "Configuracao obrigatoria ausente."
    BOTNEXT = "Falha ao consultar o BotNext."
    BOTNEXT_MESSAGES = "Falha ao consultar mensagens do BotNext."
    SYNCHRONIZATION_STAGE = "Falha ao executar etapa de sincronizacao."
    UNAVAILABLE = "Servico temporariamente indisponivel."


def operational_error(category: OperationalErrorCategory) -> str:
    if not isinstance(category, OperationalErrorCategory):
        raise ValueError("Categoria operacional invalida.")
    return category.value


SENSITIVE_ENVIRONMENT_NAMES = (
    "DATABASE_URL",
    "BOTNEXT_TOKEN",
    "BOTNEXT_CHANNEL_IDS",
)

SENSITIVE_KEY = re.compile(
    r"(?:authorization|content|dsn|message|password|secret|token|"
    r"(?:contact|message|session)_?id)$",
    re.IGNORECASE,
)

SENSITIVE_PATTERNS = (
    re.compile(r"postgres(?:ql)?://[^\s]+", re.IGNORECASE),
    re.compile(r"Bearer\s+[^\s]+", re.IGNORECASE),
    re.compile(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
        r"[0-9a-f]{4}-[0-9a-f]{12}\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?<!\d)(?:\+?\d[\s().-]*){10,15}(?!\d)"),
)


def _sensitive_values(extra_values: Iterable[object]) -> set[str]:
    values = {
        str(value)
        for value in extra_values
        if value is not None and str(value)
    }

    for name in SENSITIVE_ENVIRONMENT_NAMES:
        raw_value = os.getenv(name, "")
        if not raw_value:
            continue
        values.add(raw_value)
        if name == "BOTNEXT_CHANNEL_IDS":
            values.update(
                item.strip()
                for item in raw_value.split(",")
                if item.strip()
            )

    return values


def redact_sensitive(
    value: Any,
    *,
    extra_values: Iterable[object] = (),
) -> Any:
    """Redact sensitive runtime values while preserving container shape."""
    if isinstance(value, dict):
        return {
            key: (
                REDACTED
                if SENSITIVE_KEY.search(str(key))
                else redact_sensitive(item, extra_values=extra_values)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_sensitive(item, extra_values=extra_values) for item in value]
    if isinstance(value, tuple):
        return tuple(
            redact_sensitive(item, extra_values=extra_values)
            for item in value
        )
    if isinstance(value, set):
        return {
            redact_sensitive(item, extra_values=extra_values)
            for item in value
        }

    sanitized = str(value)
    for sensitive in sorted(
        _sensitive_values(extra_values),
        key=len,
        reverse=True,
    ):
        sanitized = sanitized.replace(sensitive, REDACTED)
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(REDACTED, sanitized)

    return sanitized
