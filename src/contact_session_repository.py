import json
from typing import Any

from src.database import conectar
from src.vendedor_service import (
    normalizar_telefone,
)


def converter_json(valor: Any) -> str:
    return json.dumps(
        valor,
        ensure_ascii=False,
        default=str,
    )


def listar_usuarios_para_identificacao(
) -> list[dict[str, Any]]:
    with conectar() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    nome,
                    nome_curto
                FROM usuarios_botnext
                WHERE nome IS NOT NULL
                   OR nome_curto IS NOT NULL
                """
            )

            registros = cursor.fetchall()

    return [
        {
            "nome": registro[0],
            "nome_curto": registro[1],
        }
        for registro in registros
    ]


def salvar_contatos(
    contatos: list[dict[str, Any]],
) -> int:
    comando = """
        INSERT INTO contatos (
            id,
            company_id,
            nome,
            nome_whatsapp,
            nome_instagram,
            telefone,
            telefone_formatado,
            telefone_normalizado,
            email,
            status,
            origem,
            carteiras_json,
            etiquetas_json,
            campos_personalizados_json,
            vendedor_responsavel,
            origem_vendedor,
            regra_vendedor,
            payload_json,
            criado_em_api,
            atualizado_em_api,
            sincronizado_em
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s::JSONB, %s::JSONB,
            %s::JSONB, %s, %s, %s,
            %s::JSONB, %s, %s, NOW()
        )
        ON CONFLICT (id)
        DO UPDATE SET
            company_id = EXCLUDED.company_id,
            nome = EXCLUDED.nome,
            nome_whatsapp = EXCLUDED.nome_whatsapp,
            nome_instagram = EXCLUDED.nome_instagram,
            telefone = EXCLUDED.telefone,
            telefone_formatado = EXCLUDED.telefone_formatado,
            telefone_normalizado = EXCLUDED.telefone_normalizado,
            email = EXCLUDED.email,
            status = EXCLUDED.status,
            origem = EXCLUDED.origem,
            carteiras_json = EXCLUDED.carteiras_json,
            etiquetas_json = EXCLUDED.etiquetas_json,
            campos_personalizados_json =
                EXCLUDED.campos_personalizados_json,
            vendedor_responsavel =
                EXCLUDED.vendedor_responsavel,
            origem_vendedor =
                EXCLUDED.origem_vendedor,
            regra_vendedor =
                EXCLUDED.regra_vendedor,
            payload_json = EXCLUDED.payload_json,
            criado_em_api = EXCLUDED.criado_em_api,
            atualizado_em_api =
                EXCLUDED.atualizado_em_api,
            sincronizado_em = NOW()
    """

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            for contato in contatos:
                cursor.execute(
                    comando,
                    (
                        contato.get("id"),
                        contato.get("companyId"),
                        contato.get("name"),
                        contato.get("nameWhatsapp"),
                        contato.get("nameInstagram"),
                        contato.get("phoneNumber"),
                        contato.get(
                            "phoneNumberFormatted"
                        ),
                        normalizar_telefone(
                            contato.get("phoneNumber")
                        ),
                        contato.get("email"),
                        contato.get("status"),
                        contato.get("origin"),
                        converter_json(
                            contato.get(
                                "portfolioNames"
                            ) or []
                        ),
                        converter_json(
                            contato.get(
                                "tagNames"
                            ) or []
                        ),
                        converter_json(
                            contato.get(
                                "customFields"
                            ) or {}
                        ),
                        contato.get(
                            "_vendedor_responsavel"
                        ),
                        contato.get(
                            "_origem_vendedor"
                        ),
                        contato.get(
                            "_regra_vendedor"
                        ),
                        converter_json(contato),
                        contato.get("createdAt"),
                        contato.get("updatedAt"),
                    ),
                )

    return len(contatos)


def salvar_sessoes(
    sessoes: list[dict[str, Any]],
) -> int:
    comando = """
        INSERT INTO sessoes (
            id,
            contact_id,
            company_id,
            user_id,
            channel_id,
            department_id,
            tipo,
            status,
            descricao_status,
            titulo,
            numero,
            origem,
            iniciada_em,
            finalizada_em,
            primeira_resposta_em,
            ultima_interacao_em,
            tempo_servico,
            tempo_espera,
            quantidade_nao_lidas,
            ultima_mensagem_texto,
            ultima_mensagem_recebida_em,
            ultima_mensagem_enviada_em,
            detalhes_json,
            payload_json,
            criado_em_api,
            atualizado_em_api,
            sincronizado_em
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s::JSONB,
            %s::JSONB, %s, %s, NOW()
        )
        ON CONFLICT (id)
        DO UPDATE SET
            contact_id = EXCLUDED.contact_id,
            company_id = EXCLUDED.company_id,
            user_id = EXCLUDED.user_id,
            channel_id = EXCLUDED.channel_id,
            department_id = EXCLUDED.department_id,
            tipo = EXCLUDED.tipo,
            status = EXCLUDED.status,
            descricao_status =
                EXCLUDED.descricao_status,
            titulo = EXCLUDED.titulo,
            numero = EXCLUDED.numero,
            origem = EXCLUDED.origem,
            iniciada_em = EXCLUDED.iniciada_em,
            finalizada_em = EXCLUDED.finalizada_em,
            primeira_resposta_em =
                EXCLUDED.primeira_resposta_em,
            ultima_interacao_em =
                EXCLUDED.ultima_interacao_em,
            tempo_servico = EXCLUDED.tempo_servico,
            tempo_espera = EXCLUDED.tempo_espera,
            quantidade_nao_lidas =
                EXCLUDED.quantidade_nao_lidas,
            ultima_mensagem_texto =
                EXCLUDED.ultima_mensagem_texto,
            ultima_mensagem_recebida_em =
                EXCLUDED.ultima_mensagem_recebida_em,
            ultima_mensagem_enviada_em =
                EXCLUDED.ultima_mensagem_enviada_em,
            detalhes_json = EXCLUDED.detalhes_json,
            payload_json = EXCLUDED.payload_json,
            criado_em_api = EXCLUDED.criado_em_api,
            atualizado_em_api =
                EXCLUDED.atualizado_em_api,
            sincronizado_em = NOW()
    """

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            for sessao in sessoes:
                detalhes = {
                    "contactDetails": sessao.get(
                        "contactDetails"
                    ),
                    "agentDetails": sessao.get(
                        "agentDetails"
                    ),
                    "channelDetails": sessao.get(
                        "channelDetails"
                    ),
                    "departmentDetails": sessao.get(
                        "departmentDetails"
                    ),
                    "classification": sessao.get(
                        "classification"
                    ),
                }

                ultima_interacao = (
                    sessao.get("lastInteractionAt")
                    or sessao.get("activeAt")
                    or sessao.get("updatedAt")
                )

                cursor.execute(
                    comando,
                    (
                        sessao.get("id"),
                        sessao.get("contactId"),
                        sessao.get("companyId"),
                        sessao.get("userId"),
                        sessao.get("channelId"),
                        sessao.get("departmentId"),
                        sessao.get("type"),
                        sessao.get("status"),
                        sessao.get(
                            "statusDescription"
                        ),
                        sessao.get("title"),
                        sessao.get("number"),
                        sessao.get("origin"),
                        sessao.get("startAt"),
                        sessao.get("endAt"),
                        sessao.get(
                            "firstResponseAt"
                        ),
                        ultima_interacao,
                        sessao.get("timeService"),
                        sessao.get("timeWait"),
                        sessao.get(
                            "unreadCount"
                        ) or 0,
                        sessao.get(
                            "lastMessageText"
                        ),
                        sessao.get("lastMessageIn"),
                        sessao.get("lastMessageOut"),
                        converter_json(detalhes),
                        converter_json(sessao),
                        sessao.get("createdAt"),
                        sessao.get("updatedAt"),
                    ),
                )

    return len(sessoes)