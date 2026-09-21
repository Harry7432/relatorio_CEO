import re
import unicodedata
from typing import Any


MAPA_ETIQUETAS_VENDEDORES = {
    "parcerias vini": "Vinicius Macedo",
    "quinzenal ricardo 1": "Ricardo",
}


def normalizar_texto(
    valor: str | None,
) -> str:
    if not valor:
        return ""

    texto = unicodedata.normalize(
        "NFD",
        valor,
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    texto = texto.casefold().strip()

    return " ".join(texto.split())


def normalizar_telefone(
    telefone: str | None,
) -> str | None:
    if not telefone:
        return None

    numeros = re.sub(
        r"\D",
        "",
        telefone,
    )

    return numeros or None


def construir_mapa_usuarios(
    usuarios: list[dict[str, Any]],
) -> dict[str, set[str]]:
    mapa: dict[str, set[str]] = {}

    for usuario in usuarios:
        nome = usuario.get("nome")
        nome_curto = usuario.get("nome_curto")

        nome_exibicao = nome or nome_curto

        if not nome_exibicao:
            continue

        for variacao in [nome, nome_curto]:
            chave = normalizar_texto(
                variacao
            )

            if not chave:
                continue

            mapa.setdefault(
                chave,
                set(),
            ).add(
                nome_exibicao
            )

    return mapa


def identificar_vendedor(
    contato: dict[str, Any],
    mapa_usuarios: dict[str, set[str]],
) -> tuple[str, str, str]:
    carteiras = contato.get(
        "portfolioNames"
    ) or []

    carteiras_unicas = list(
        dict.fromkeys(
            carteira.strip()
            for carteira in carteiras
            if carteira and carteira.strip()
        )
    )

    if len(carteiras_unicas) == 1:
        return (
            carteiras_unicas[0],
            "CARTEIRA",
            "Única carteira encontrada",
        )

    if len(carteiras_unicas) > 1:
        return (
            " | ".join(carteiras_unicas),
            "CARTEIRA_MULTIPLA",
            "Mais de uma carteira encontrada",
        )

    etiquetas = contato.get(
        "tagNames"
    ) or []

    vendedores_manuais: set[str] = set()

    for etiqueta in etiquetas:
        chave = normalizar_texto(
            etiqueta
        )

        vendedor_mapeado = (
            MAPA_ETIQUETAS_VENDEDORES.get(
                chave
            )
        )

        if vendedor_mapeado:
            vendedores_manuais.add(
                vendedor_mapeado
            )

    if len(vendedores_manuais) == 1:
        return (
            next(iter(vendedores_manuais)),
            "ETIQUETA_MAPEADA",
            "Etiqueta definida no mapa manual",
        )

    if len(vendedores_manuais) > 1:
        return (
            " | ".join(
                sorted(vendedores_manuais)
            ),
            "ETIQUETA_MULTIPLA",
            "Mais de uma etiqueta mapeada",
        )

    vendedores_encontrados: set[str] = set()

    for etiqueta in etiquetas:
        chave = normalizar_texto(
            etiqueta
        )

        vendedores = mapa_usuarios.get(
            chave,
            set(),
        )

        vendedores_encontrados.update(
            vendedores
        )

    vendedores_ordenados = sorted(
        vendedores_encontrados
    )

    if len(vendedores_ordenados) == 1:
        return (
            vendedores_ordenados[0],
            "ETIQUETA",
            "Etiqueta igual ao nome de um usuário",
        )

    if len(vendedores_ordenados) > 1:
        return (
            " | ".join(
                vendedores_ordenados
            ),
            "ETIQUETA_MULTIPLA",
            "Mais de uma etiqueta de vendedor",
        )

    return (
        "Não identificado",
        "NAO_IDENTIFICADO",
        "Sem carteira ou etiqueta de vendedor",
    )