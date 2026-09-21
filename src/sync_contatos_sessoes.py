import time

from src.botnext_client import BotNextClient
from src.contact_session_repository import (
    listar_usuarios_para_identificacao,
    salvar_contatos,
    salvar_sessoes,
)
from src.vendedor_service import (
    construir_mapa_usuarios,
    identificar_vendedor,
)


INTERVALO_ENTRE_REQUISICOES = 0.35


def main() -> None:
    print(
        "Iniciando sincronização completa "
        "de contatos e sessões..."
    )

    cliente = BotNextClient()

    try:
        sessoes_por_id: dict[str, dict] = {}

        print(
            "Buscando a primeira página "
            "de sessões..."
        )

        primeira_pagina = (
            cliente.listar_sessoes_pagina(
                pagina=1
            )
        )

        total_paginas = (
            primeira_pagina.get(
                "totalPages"
            )
            or 1
        )

        total_informado = (
            primeira_pagina.get(
                "totalItems"
            )
            or 0
        )

        print(
            f"Sessões informadas pela API: "
            f"{total_informado}"
        )

        print(
            f"Total de páginas: "
            f"{total_paginas}"
        )

        for pagina in range(
            1,
            total_paginas + 1,
        ):
            if pagina == 1:
                resultado = primeira_pagina

            else:
                resultado = (
                    cliente.listar_sessoes_pagina(
                        pagina=pagina
                    )
                )

            itens = (
                resultado.get("items")
                or []
            )

            for sessao in itens:
                session_id = sessao.get("id")

                if session_id:
                    sessoes_por_id[
                        session_id
                    ] = sessao

            print(
                f"Página "
                f"{pagina}/{total_paginas}: "
                f"{len(itens)} sessões"
            )

        sessoes = list(
            sessoes_por_id.values()
        )

        print(
            "\nSessões únicas coletadas: "
            f"{len(sessoes)}"
        )

        usuarios = (
            listar_usuarios_para_identificacao()
        )

        mapa_usuarios = (
            construir_mapa_usuarios(
                usuarios
            )
        )

        contact_ids = sorted(
            {
                sessao.get("contactId")
                for sessao in sessoes
                if sessao.get("contactId")
            }
        )

        total_contatos = len(contact_ids)

        print(
            "Contatos únicos para consultar: "
            f"{total_contatos}"
        )

        contatos: list[dict] = []

        for indice, contact_id in enumerate(
            contact_ids,
            start=1,
        ):
            if (
                indice == 1
                or indice % 10 == 0
                or indice == total_contatos
            ):
                print(
                    f"Consultando contato "
                    f"{indice}/{total_contatos}"
                )

            contato = (
                cliente.obter_contato(
                    contact_id
                )
            )

            (
                vendedor,
                origem_vendedor,
                regra_vendedor,
            ) = identificar_vendedor(
                contato,
                mapa_usuarios,
            )

            contato[
                "_vendedor_responsavel"
            ] = vendedor

            contato[
                "_origem_vendedor"
            ] = origem_vendedor

            contato[
                "_regra_vendedor"
            ] = regra_vendedor

            contatos.append(contato)

            if indice < total_contatos:
                time.sleep(
                    INTERVALO_ENTRE_REQUISICOES
                )

        print("\nGravando contatos...")

        quantidade_contatos = (
            salvar_contatos(
                contatos
            )
        )

        print(
            "Contatos gravados/atualizados: "
            f"{quantidade_contatos}"
        )

        print("Gravando sessões...")

        quantidade_sessoes = (
            salvar_sessoes(
                sessoes
            )
        )

        print(
            "Sessões gravadas/atualizadas: "
            f"{quantidade_sessoes}"
        )

        print(
            "\nSincronização completa de "
            "contatos e sessões concluída!"
        )

    finally:
        cliente.fechar()


if __name__ == "__main__":
    main()