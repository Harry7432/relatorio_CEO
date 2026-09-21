from src.botnext_client import BotNextClient


def main() -> None:
    print(
        "Buscando uma sessão para testar "
        "contato e mensagens..."
    )

    cliente = BotNextClient()

    try:
        pagina_sessoes = (
            cliente.listar_sessoes_pagina(
                pagina=1
            )
        )

        sessoes = pagina_sessoes.get("items") or []

        if not sessoes:
            raise RuntimeError(
                "Nenhuma sessão foi encontrada."
            )

        sessao = sessoes[0]

        session_id = sessao.get("id")
        contact_id = sessao.get("contactId")

        if not session_id:
            raise RuntimeError(
                "A sessão não possui ID."
            )

        if not contact_id:
            raise RuntimeError(
                "A sessão não possui contactId."
            )

        print("\nSessão selecionada:")
        print(f"ID: {session_id}")
        print(f"Título: {sessao.get('title')}")
        print(f"Contato ID: {contact_id}")
        print(f"Canal ID: {sessao.get('channelId')}")

        contato = cliente.obter_contato(
            contact_id
        )

        print("\nContato encontrado:")
        print(f"Nome: {contato.get('name')}")
        print(
            f"WhatsApp: "
            f"{contato.get('nameWhatsapp')}"
        )
        print(
            f"Telefone: "
            f"{contato.get('phoneNumber')}"
        )
        print(
            f"Carteiras: "
            f"{contato.get('portfolioNames')}"
        )
        print(
            f"Etiquetas: "
            f"{contato.get('tagNames')}"
        )

        pagina_mensagens = (
            cliente.listar_mensagens_pagina(
                session_id=session_id,
                pagina=1,
            )
        )

        mensagens = (
            pagina_mensagens.get("items") or []
        )

        print("\nMensagens da sessão:")
        print(
            f"Total: "
            f"{pagina_mensagens.get('totalItems')}"
        )
        print(
            f"Páginas: "
            f"{pagina_mensagens.get('totalPages')}"
        )

        print("\nPrimeiras mensagens:")

        for mensagem in mensagens[:5]:
            print("-" * 50)
            print(f"ID: {mensagem.get('id')}")
            print(
                f"Data: "
                f"{mensagem.get('timestamp')}"
            )
            print(
                f"Tipo: "
                f"{mensagem.get('type')}"
            )
            print(
                f"Direção: "
                f"{mensagem.get('direction')}"
            )
            print(
                f"Usuário: "
                f"{mensagem.get('userId')}"
            )
            print(
                f"Texto: "
                f"{mensagem.get('text')}"
            )

        print(
            "\nTeste de contato e mensagens "
            "concluído com sucesso!"
        )

    finally:
        cliente.fechar()


if __name__ == "__main__":
    main()