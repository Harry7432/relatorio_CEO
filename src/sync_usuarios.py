from src.botnext_client import BotNextClient
from src.repositories import salvar_usuarios


def main() -> None:
    print("Buscando usuários do BotNext...")

    cliente = BotNextClient()

    try:
        usuarios = cliente.listar_usuarios()

        print(
            f"Usuários retornados pela API: "
            f"{len(usuarios)}"
        )

        quantidade = salvar_usuarios(
            usuarios
        )

        print(
            f"Usuários gravados no banco: "
            f"{quantidade}"
        )

        print(
            "\nSincronização de usuários concluída!"
        )

    finally:
        cliente.fechar()


if __name__ == "__main__":
    main()