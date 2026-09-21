import json
from typing import Any

from src.database import conectar


def converter_json(
    valor: Any,
) -> str:
    return json.dumps(
        valor,
        ensure_ascii=False,
        default=str,
    )


def listar_sessoes(
    limite: int | None = None,
) -> list[str]:
    comando = """
        SELECT id
        FROM sessoes
        ORDER BY criado_em_api ASC, id ASC
    """

    parametros: tuple = ()

    if limite is not None:
        comando += " LIMIT %s"
        parametros = (limite,)

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                comando,
                parametros,
            )

            registros = cursor.fetchall()

    return [
        str(registro[0])
        for registro in registros
    ]


def salvar_mensagens(
    mensagens: list[dict[str, Any]],
) -> int:
    if not mensagens:
        return 0

    comando = """
        INSERT INTO mensagens (
            id,
            session_id,
            user_id,
            sender_id,
            template_id,
            tipo,
            direcao,
            status,
            origem,
            texto,
            timestamp_mensagem,
            criado_em_api,
            atualizado_em_api,
            lido_pelo_contato_em,
            file_id,
            ref_id,
            motivo_falha,
            categoria_template,
            texto_rodape,
            detalhes_json,
            arquivos_json,
            payload_json,
            sincronizado_em
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s::JSONB,
            %s::JSONB,
            %s::JSONB,
            NOW()
        )
        ON CONFLICT (id)
        DO UPDATE SET
            session_id =
                EXCLUDED.session_id,
            user_id =
                EXCLUDED.user_id,
            sender_id =
                EXCLUDED.sender_id,
            template_id =
                EXCLUDED.template_id,
            tipo =
                EXCLUDED.tipo,
            direcao =
                EXCLUDED.direcao,
            status =
                EXCLUDED.status,
            origem =
                EXCLUDED.origem,
            texto =
                EXCLUDED.texto,
            timestamp_mensagem =
                EXCLUDED.timestamp_mensagem,
            criado_em_api =
                EXCLUDED.criado_em_api,
            atualizado_em_api =
                EXCLUDED.atualizado_em_api,
            lido_pelo_contato_em =
                EXCLUDED.lido_pelo_contato_em,
            file_id =
                EXCLUDED.file_id,
            ref_id =
                EXCLUDED.ref_id,
            motivo_falha =
                EXCLUDED.motivo_falha,
            categoria_template =
                EXCLUDED.categoria_template,
            texto_rodape =
                EXCLUDED.texto_rodape,
            detalhes_json =
                EXCLUDED.detalhes_json,
            arquivos_json =
                EXCLUDED.arquivos_json,
            payload_json =
                EXCLUDED.payload_json,
            sincronizado_em = NOW()
    """

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            for mensagem in mensagens:
                detalhes = (
                    mensagem.get("details")
                    or {}
                )

                arquivos = (
                    detalhes.get("files")
                    or mensagem.get("filesIds")
                    or []
                )

                timestamp_mensagem = (
                    mensagem.get("timestamp")
                    or mensagem.get("createdAt")
                )

                cursor.execute(
                    comando,
                    (
                        mensagem.get("id"),
                        mensagem.get(
                            "sessionId"
                        ),
                        mensagem.get("userId"),
                        mensagem.get("senderId"),
                        mensagem.get(
                            "templateId"
                        ),
                        mensagem.get("type"),
                        mensagem.get(
                            "direction"
                        ),
                        mensagem.get("status"),
                        mensagem.get("origin"),
                        mensagem.get("text"),
                        timestamp_mensagem,
                        mensagem.get(
                            "createdAt"
                        ),
                        mensagem.get(
                            "updatedAt"
                        ),
                        mensagem.get(
                            "readContactAt"
                        ),
                        mensagem.get("fileId"),
                        mensagem.get("refId"),
                        mensagem.get(
                            "failedReason"
                        ),
                        detalhes.get(
                            "templateCategoryName"
                        ),
                        detalhes.get(
                            "footerText"
                        ),
                        converter_json(
                            detalhes
                        ),
                        converter_json(
                            arquivos
                        ),
                        converter_json(
                            mensagem
                        ),
                    ),
                )

    return len(mensagens)