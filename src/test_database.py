from src.database import testar_conexao


def main() -> None:
    print("Testando conexão com o PostgreSQL...")

    try:
        resultado = testar_conexao()

        informacoes = resultado["informacoes"]
        tabelas = resultado["tabelas"]

        print("\nConexão realizada com sucesso!")
        print(f"Banco: {informacoes['banco']}")
        print(f"Usuário: {informacoes['usuario']}")
        print(f"Esquema: {informacoes['esquema']}")
        print(
            "Horário do servidor: "
            f"{informacoes['horario_servidor']}"
        )

        print("\nTabelas encontradas:")

        for tabela in tabelas:
            print(f"- {tabela}")

    except Exception as erro:
        print("\nNão foi possível conectar ao banco.")
        print(f"Erro: {erro}")
        raise


if __name__ == "__main__":
    main()