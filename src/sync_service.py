import os
import subprocess
import sys

from collections.abc import Callable
from pathlib import Path


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
        detalhes = (
            resultado.stderr.strip()
            or resultado.stdout.strip()
            or "Nenhum detalhe retornado."
        )

        raise RuntimeError(
            f"Falha ao executar {modulo}:\n"
            f"{detalhes[-4000:]}"
        )

    return resultado.stdout


def executar_sincronizacao_completa(
    atualizar_progresso: (
        Callable[[int, int, str], None] | None
    ) = None,
) -> list[str]:
    logs: list[str] = []

    total_etapas = len(
        ETAPAS_SINCRONIZACAO
    )

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

        logs.append(
            f"{descricao}:\n{saida}"
        )

        if atualizar_progresso:
            atualizar_progresso(
                indice + 1,
                total_etapas,
                descricao,
            )

    return logs