import os
import re

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "")

DB_SCHEMA = os.getenv(
    "DB_SCHEMA",
    "app",
)

BOTNEXT_CHAT_URL = os.getenv(
    "BOTNEXT_CHAT_URL",
    "https://chat-api.example.invalid",
)

BOTNEXT_CORE_URL = os.getenv(
    "BOTNEXT_CORE_URL",
    "https://chat-api.example.invalid",
)

BOTNEXT_TOKEN = os.getenv("BOTNEXT_TOKEN", "")

PAGE_SIZE = int(
    os.getenv("PAGE_SIZE", "100")
)

SYNC_DAYS_BACK = int(
    os.getenv("SYNC_DAYS_BACK", "60")
)

LOCAL_TIMEZONE = os.getenv(
    "LOCAL_TIMEZONE",
    "America/Sao_Paulo",
)

BOTNEXT_CHANNEL_IDS = [
    channel_id.strip()
    for channel_id in os.getenv(
        "BOTNEXT_CHANNEL_IDS",
        "",
    ).split(",")
    if channel_id.strip()
]


def validar_configuracoes_banco() -> None:
    if not DATABASE_URL:
        raise ValueError(
            "Configuracao ausente: DATABASE_URL."
        )

    schema_valido = re.fullmatch(
        r"[a-z_][a-z0-9_]*",
        DB_SCHEMA,
    )

    if not schema_valido:
        raise ValueError(
            "Configuracao invalida: DB_SCHEMA."
        )


def validar_configuracoes_botnext() -> None:
    if not BOTNEXT_TOKEN:
        raise ValueError(
            "Configuracao ausente: BOTNEXT_TOKEN."
        )

    if not BOTNEXT_CHANNEL_IDS:
        raise ValueError(
            "Configuracao ausente: BOTNEXT_CHANNEL_IDS."
        )

    if PAGE_SIZE < 1 or PAGE_SIZE > 100:
        raise ValueError(
            "PAGE_SIZE deve estar entre 1 e 100."
        )

    if SYNC_DAYS_BACK < 1:
        raise ValueError(
            "SYNC_DAYS_BACK deve ser maior que zero."
        )
