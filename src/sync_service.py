import os
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from src import sync_lock
from src.runtime_security import (
    OperationalErrorCategory,
    operational_error,
    redact_sensitive,
)

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

ETAPAS_SINCRONIZACAO = [
    (
        "Sincronizando usuários",
        "src.sync_usuarios",
    ),
    (
        "Sincronizando contatos e sessões",
        "src.sync_contatos_sessoes",
    ),
    (
        "Sincronizando mensagens",
        "src.sync_mensagens",
    ),
]


def executar_modulo(
    modulo: str,
) -> str:
    ambiente = os.environ.copy()
    ambiente["PYTHONIOENCODING"] = "utf-8"

    resultado = subprocess.run(
        [
            sys.executable,
            "-m",
            modulo,
        ],
        cwd=RAIZ_PROJETO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ambiente,
        timeout=3600,
        check=False,
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            operational_error(
                OperationalErrorCategory.SYNCHRONIZATION_STAGE
            )
        )

    return "Etapa concluida com sucesso."


def executar_sincronizacao_completa(
    atualizar_progresso: (
        Callable[[int, int, str], None] | None
    ) = None,
    conexao_lock: Any | None = None,
) -> list[str]:
    run_id = f"sync_{uuid.uuid4().hex[:12]}"
    logs: list[str] = []

    with sync_lock.obter_lock_sincronizacao(
        conexao_custom=conexao_lock
    ) as adquirido:
        if not adquirido:
            msg_skipped = (
                f"[SYNC_RUN] run_id={run_id} status=skipped_concurrency "
                f"message=\"Lock de sincronizacao ja adquirido por outra execucao.\""
            )
            print(msg_skipped)
            return []

        inicio = time.time()
        print(f"[SYNC_RUN] run_id={run_id} status=started stage=init")

        total_etapas = len(
            ETAPAS_SINCRONIZACAO
        )

        try:
            for indice, (
                descricao,
                modulo,
            ) in enumerate(
                ETAPAS_SINCRONIZACAO
            ):
                if atualizar_progresso:
                    atualizar_progresso(
                        indice,
                        total_etapas,
                        descricao,
                    )

                saida = executar_modulo(modulo)
                saida_sanitizada = redact_sensitive(saida)

                log_etapa = (
                    f"{descricao}:\n{saida_sanitizada}"
                )
                logs.append(log_etapa)

                if atualizar_progresso:
                    atualizar_progresso(
                        indice + 1,
                        total_etapas,
                        descricao,
                    )

            duracao = time.time() - inicio
            print(
                f"[SYNC_RUN] run_id={run_id} status=success "
                f"stage=completed duration_seconds={duracao:.2f}"
            )
            return logs

        except Exception as exc:
            erro_sanitizado = redact_sensitive(
                str(exc)
            )
            print(
                f"[SYNC_RUN] run_id={run_id} status=failed "
                f"error=\"{erro_sanitizado}\""
            )
            raise


def main() -> None:
    try:
        logs = executar_sincronizacao_completa()
        for log in logs:
            print(redact_sensitive(log))
    except Exception as exc:
        print(
            redact_sensitive(
                f"Falha na sincronizacao: {exc}"
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
