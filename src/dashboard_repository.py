from typing import Any

from src.config import DB_SCHEMA
from src.database import conectar


def buscar_dados_dashboard() -> list[dict[str, Any]]:
    sql = f"""
        SELECT
            mensagem.id AS mensagem_id,
            mensagem.session_id AS sessao_id,
            mensagem.user_id AS usuario_id_mensagem,
            mensagem.timestamp_mensagem,
            mensagem.tipo AS tipo_mensagem,
            mensagem.direcao,
            mensagem.status AS status_mensagem,
            mensagem.origem AS origem_mensagem,
            mensagem.texto,

            sessao.status AS status_sessao,
            sessao.channel_id,
            sessao.titulo AS titulo_sessao,
            sessao.numero AS numero_sessao,

            contato.id AS contato_id,
            contato.nome AS contato_nome,
            contato.nome_whatsapp,
            contato.telefone,
            contato.telefone_formatado,
            contato.vendedor_responsavel,
            contato.origem_vendedor,

            usuario.nome AS usuario_mensagem

        FROM {DB_SCHEMA}.mensagens AS mensagem

        INNER JOIN {DB_SCHEMA}.sessoes AS sessao
            ON sessao.id = mensagem.session_id

        LEFT JOIN {DB_SCHEMA}.contatos AS contato
            ON contato.id = sessao.contact_id

        LEFT JOIN {DB_SCHEMA}.usuarios_botnext AS usuario
            ON usuario.user_id = mensagem.user_id

        ORDER BY
            mensagem.timestamp_mensagem DESC;
    """

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql)

            colunas = [
                descricao.name
                for descricao in cursor.description
            ]

            registros = cursor.fetchall()

    return [
        dict(zip(colunas, registro))
        for registro in registros
    ]


def buscar_resumo_banco() -> dict[str, int]:
    sql = f"""
        SELECT
            (
                SELECT COUNT(*)
                FROM {DB_SCHEMA}.usuarios_botnext
            ) AS usuarios,

            (
                SELECT COUNT(*)
                FROM {DB_SCHEMA}.contatos
            ) AS contatos,

            (
                SELECT COUNT(*)
                FROM {DB_SCHEMA}.sessoes
            ) AS sessoes,

            (
                SELECT COUNT(*)
                FROM {DB_SCHEMA}.mensagens
            ) AS mensagens;
    """

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql)
            registro = cursor.fetchone()

    if registro is None:
        return {
            "usuarios": 0,
            "contatos": 0,
            "sessoes": 0,
            "mensagens": 0,
        }

    return {
        "usuarios": registro[0],
        "contatos": registro[1],
        "sessoes": registro[2],
        "mensagens": registro[3],
    }
