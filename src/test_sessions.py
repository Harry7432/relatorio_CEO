from src.botnext_client import BotNextClient
from src.config import (
    BOTNEXT_CHANNEL_IDS,
    SYNC_DAYS_BACK,
)


def main() -> None:
    print("Testando consulta de sessões do BotNext...")
    print(f"Período: últimos {SYNC_DAYS_BACK} dias")

    print("Canais:")

    for channel_id in BOTNEXT_CHANNEL_IDS:
        print(f"- {channel_id}")

    cliente = BotNextClient()

    try:
        resultado = cliente.listar_sessoes_pagina(
            pagina=1
        )

        itens = resultado.get("items") or []

        print("\nConsulta realizada com sucesso!")
        print(
            f"Página: {resultado.get('pageNumber')}"
        )
        print(
            f"Tamanho da página: "
            f"{resultado.get('pageSize')}"
        )
        print(
            f"Total de sessões: "
            f"{resultado.get('totalItems')}"
        )
        print(
            f"Total de páginas: "
            f"{resultado.get('totalPages')}"
        )
        print(
            f"Possui mais páginas: "
            f"{resultado.get('hasMorePages')}"
        )

        print("\nPrimeiras sessões encontradas:")

        for sessao in itens[:5]:
            print("-" * 50)
            print(f"ID: {sessao.get('id')}")
            print(
                f"Contato: {sessao.get('contactId')}"
            )
            print(
                f"Canal: {sessao.get('channelId')}"
            )
            print(
                f"Número: {sessao.get('number')}"
            )
            print(
                f"Status: {sessao.get('status')}"
            )
            print(
                "Última interação: "
                f"{sessao.get('lastInteractionAt')}"
            )
            print(
                f"Título: {sessao.get('title')}"
            )

    finally:
        cliente.fechar()


if __name__ == "__main__":
    main()