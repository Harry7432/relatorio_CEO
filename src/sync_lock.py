from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

SYNC_ADVISORY_LOCK_ID = 8573920194821


def tentar_adquirir_lock(
    conexao: Any,
    lock_id: int = SYNC_ADVISORY_LOCK_ID,
) -> bool:
    with conexao.cursor() as cursor:
        cursor.execute(
            "SELECT pg_try_advisory_lock(%s)",
            (lock_id,),
        )
        resultado = cursor.fetchone()
        if resultado and len(resultado) > 0:
            return bool(resultado[0])
        return False


def liberar_lock(
    conexao: Any,
    lock_id: int = SYNC_ADVISORY_LOCK_ID,
) -> bool:
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_unlock(%s)",
                (lock_id,),
            )
            resultado = cursor.fetchone()
            if resultado and len(resultado) > 0:
                return bool(resultado[0])
            return False
    except Exception:
        return False


@contextmanager
def obter_lock_sincronizacao(
    conexao_custom: Any | None = None,
    lock_id: int = SYNC_ADVISORY_LOCK_ID,
) -> Generator[bool, None, None]:
    if conexao_custom is not None:
        adquirido = tentar_adquirir_lock(
            conexao_custom,
            lock_id=lock_id,
        )
        try:
            yield adquirido
        finally:
            if adquirido:
                liberar_lock(
                    conexao_custom,
                    lock_id=lock_id,
                )
    else:
        try:
            from src.database import conectar

            with conectar() as conexao:
                adquirido = tentar_adquirir_lock(
                    conexao,
                    lock_id=lock_id,
                )
                try:
                    yield adquirido
                finally:
                    if adquirido:
                        liberar_lock(
                            conexao,
                            lock_id=lock_id,
                        )
        except Exception:
            yield True
