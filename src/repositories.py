import json
from typing import Any

from src.database import conectar


def converter_json(valor: Any) -> str:
    return json.dumps(
        valor,
        ensure_ascii=False,
        default=str,
    )


def salvar_usuarios(
    usuarios: list[dict[str, Any]],
) -> int:
    quantidade = 0

    comando = """
        INSERT INTO usuarios_botnext (
            id,
            user_id,
            company_id,
            nome,
            nome_curto,
            email,
            telefone,
            telefone_formatado,
            perfil,
            is_owner,
            disponibilidade,
            departamentos_json,
            payload_json,
            criado_em_api,
            atualizado_em_api,
            sincronizado_em
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s::JSONB,
            %s::JSONB,
            %s,
            %s,
            NOW()
        )
        ON CONFLICT (id)
        DO UPDATE SET
            user_id = EXCLUDED.user_id,
            company_id = EXCLUDED.company_id,
            nome = EXCLUDED.nome,
            nome_curto = EXCLUDED.nome_curto,
            email = EXCLUDED.email,
            telefone = EXCLUDED.telefone,
            telefone_formatado = EXCLUDED.telefone_formatado,
            perfil = EXCLUDED.perfil,
            is_owner = EXCLUDED.is_owner,
            disponibilidade = EXCLUDED.disponibilidade,
            departamentos_json = EXCLUDED.departamentos_json,
            payload_json = EXCLUDED.payload_json,
            criado_em_api = EXCLUDED.criado_em_api,
            atualizado_em_api = EXCLUDED.atualizado_em_api,
            sincronizado_em = NOW()
    """

    with conectar() as conexao:
        with conexao.cursor() as cursor:
            for usuario in usuarios:
                cursor.execute(
                    comando,
                    (
                        usuario.get("id"),
                        usuario.get("userId"),
                        usuario.get("companyId"),
                        usuario.get("name"),
                        usuario.get("shortName"),
                        usuario.get("email"),
                        usuario.get("phoneNumber"),
                        usuario.get(
                            "phoneNumberFormatted"
                        ),
                        usuario.get("profile"),
                        usuario.get("isOwner", False),
                        usuario.get("availability"),
                        converter_json(
                            usuario.get("departments") or []
                        ),
                        converter_json(usuario),
                        usuario.get("createdAt"),
                        usuario.get("updatedAt"),
                    ),
                )

                quantidade += 1

    return quantidade