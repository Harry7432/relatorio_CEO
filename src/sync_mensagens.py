import argparse
import time
from typing import Any

from src.botnext_client import BotNextClient
from src.runtime_security import OperationalErrorCategory, operational_error
from src.message_repository import (
    listar_sessoes,
    salvar_mensagens,
)


INTERVALO_REQUISICOES = 0.35
TAMANHO_LOTE_BANCO = 500
QUANTIDADE_TENTATIVAS = 5


def obter_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sincroniza mensagens do BotNext."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Limita a quantidade de sessões. "
            "Omita para processar todas."
        ),
    )

    return parser.parse_args()


def buscar_pagina_com_tentativas(
    cliente: BotNextClient,
    session_id: str,
    pagina: int,
) -> dict[str, Any]:
    for tentativa in range(
        1,
        QUANTIDADE_TENTATIVAS + 1,
    ):
        try:
            return (
                cliente.listar_mensagens_pagina(
                    session_id=session_id,
                    pagina=pagina,
                )
            )

        except Exception:
            if tentativa == QUANTIDADE_TENTATIVAS:
                raise RuntimeError(
                    operational_error(
                        OperationalErrorCategory.BOTNEXT_MESSAGES
                    )
                ) from None

            espera = tentativa * 5

            print(
                "\nFalha temporária. "
                f"Tentativa {tentativa}/"
                f"{QUANTIDADE_TENTATIVAS}. "
                f"Aguardando {espera}s."
            )

            time.sleep(espera)

    raise RuntimeError(
        "Não foi possível consultar a página."
    )


def main() -> None:
    argumentos = obter_argumentos()

    limite = argumentos.limit

    if limite:
        print(
            "Executando teste limitado a "
            f"{limite} sessões."
        )
    else:
        print(
            "Executando sincronização completa "
            "de mensagens."
        )

    sessoes = listar_sessoes(
        limite=limite
    )

    total_sessoes = len(sessoes)

    print(
        f"Sessões para processar: "
        f"{total_sessoes}"
    )

    cliente = BotNextClient()

    lote: list[dict[str, Any]] = []

    mensagens_encontradas = 0
    mensagens_gravadas = 0
    sessoes_com_erro: list[str] = []

    try:
        for indice, session_id in enumerate(
            sessoes,
            start=1,
        ):
            try:
                pagina = 1

                while True:
                    resultado = (
                        buscar_pagina_com_tentativas(
                            cliente=cliente,
                            session_id=session_id,
                            pagina=pagina,
                        )
                    )

                    mensagens = (
                        resultado.get("items")
                        or []
                    )

                    for mensagem in mensagens:
                        if not mensagem.get(
                            "sessionId"
                        ):
                            mensagem[
                                "sessionId"
                            ] = session_id

                    lote.extend(mensagens)

                    mensagens_encontradas += len(
                        mensagens
                    )

                    if len(lote) >= TAMANHO_LOTE_BANCO:
                        mensagens_gravadas += (
                            salvar_mensagens(lote)
                        )

                        lote.clear()

                    possui_mais_paginas = (
                        resultado.get(
                            "hasMorePages"
                        )
                        is True
                    )

                    if not possui_mais_paginas:
                        break

                    pagina += 1

                    time.sleep(
                        INTERVALO_REQUISICOES
                    )

            except Exception:
                sessoes_com_erro.append(
                    session_id
                )

                print(
                    "\nFalha ao processar uma sessao."
                )

            if (
                indice == 1
                or indice % 10 == 0
                or indice == total_sessoes
            ):
                print(
                    f"Sessões: "
                    f"{indice}/{total_sessoes} | "
                    f"Mensagens encontradas: "
                    f"{mensagens_encontradas}"
                )

            if indice < total_sessoes:
                time.sleep(
                    INTERVALO_REQUISICOES
                )

        if lote:
            mensagens_gravadas += (
                salvar_mensagens(lote)
            )

            lote.clear()

        print(
            "\nSincronização de mensagens "
            "concluída!"
        )

        print(
            f"Mensagens encontradas: "
            f"{mensagens_encontradas}"
        )

        print(
            f"Mensagens gravadas/atualizadas: "
            f"{mensagens_gravadas}"
        )

        print(
            f"Sessões com erro: "
            f"{len(sessoes_com_erro)}"
        )

    finally:
        cliente.fechar()


if __name__ == "__main__":
    main()
