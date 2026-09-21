from collections.abc import Generator
from contextlib import contextmanager

import psycopg
from psycopg import Connection, sql
from psycopg.rows import dict_row

from src.config import (
    DATABASE_URL,
    DB_SCHEMA,
    validar_configuracoes_banco,
)


@contextmanager
def conectar() -> Generator[Connection, None, None]:
    validar_configuracoes_banco()

    conexao = psycopg.connect(
        DATABASE_URL,
        connect_timeout=10,
    )

    try:
        with conexao.cursor() as cursor:
            comando_schema = sql.SQL(
                "SET search_path TO {}, public"
            ).format(
                sql.Identifier(DB_SCHEMA)
            )

            cursor.execute(comando_schema)

        yield conexao
        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def testar_conexao() -> dict:
    with conectar() as conexao:
        with conexao.cursor(
            row_factory=dict_row
        ) as cursor:
            cursor.execute(
                """
                SELECT
                    current_database() AS banco,
                    current_user AS usuario,
                    current_schema() AS esquema,
                    NOW() AS horario_servidor
                """
            )

            informacoes = cursor.fetchone()

            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name
                """,
                (DB_SCHEMA,),
            )

            tabelas = [
                registro["table_name"]
                for registro in cursor.fetchall()
            ]

    return {
        "informacoes": informacoes,
        "tabelas": tabelas,
    }