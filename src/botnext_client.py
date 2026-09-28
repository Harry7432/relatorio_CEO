from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from src.runtime_security import OperationalErrorCategory, operational_error
from src.config import (
    BOTNEXT_CHANNEL_IDS,
    BOTNEXT_CHAT_URL,
    BOTNEXT_CORE_URL,
    BOTNEXT_TOKEN,
    PAGE_SIZE,
    SYNC_DAYS_BACK,
    validar_configuracoes_botnext,
)


class BotNextClient:
    def __init__(self) -> None:
        validar_configuracoes_botnext()

        self.chat_url = BOTNEXT_CHAT_URL.rstrip("/")
        self.core_url = BOTNEXT_CORE_URL.rstrip("/")

        self.http = requests.Session()

        self.http.headers.update(
            {
                "Authorization": (
                    f"Bearer {BOTNEXT_TOKEN}"
                ),
                "Accept": "application/json",
            }
        )

    @staticmethod
    def calcular_periodo(
    ) -> tuple[datetime, datetime]:
        data_final = datetime.now(
            timezone.utc
        )

        data_inicial = (
            data_final
            - timedelta(
                days=SYNC_DAYS_BACK
            )
        )

        return data_inicial, data_final

    @staticmethod
    def formatar_data(
        data: datetime,
    ) -> str:
        return (
            data.isoformat(
                timespec="milliseconds"
            )
            .replace(
                "+00:00",
                "Z",
            )
        )

    def executar_get(
        self,
        url: str,
        parametros: (
            list[tuple[str, str | int]]
            | None
        ) = None,
    ) -> Any:
        resposta = self.http.get(
            url,
            params=parametros,
            timeout=(10, 60),
        )

        try:
            resposta.raise_for_status()

        except requests.HTTPError:
            raise RuntimeError(
                operational_error(OperationalErrorCategory.BOTNEXT)
            ) from None

        return resposta.json()

    def listar_usuarios(
        self,
    ) -> list[dict[str, Any]]:
        dados = self.executar_get(
            f"{self.core_url}/v1/agent"
        )

        if not isinstance(dados, list):
            raise RuntimeError(
                "O retorno de usuários "
                "não é uma lista."
            )

        return dados

    def listar_sessoes_pagina(
        self,
        pagina: int = 1,
    ) -> dict[str, Any]:
        data_inicial, data_final = (
            self.calcular_periodo()
        )

        parametros: list[
            tuple[str, str | int]
        ] = [
            (
                "LastInteractionAt.After",
                self.formatar_data(
                    data_inicial
                ),
            ),
            (
                "LastInteractionAt.Before",
                self.formatar_data(
                    data_final
                ),
            ),
            (
                "PageNumber",
                pagina,
            ),
            (
                "PageSize",
                PAGE_SIZE,
            ),
            (
                "OrderBy",
                "CreatedAt",
            ),
            (
                "OrderDirection",
                "ASCENDING",
            ),
        ]

        for channel_id in (
            BOTNEXT_CHANNEL_IDS
        ):
            parametros.append(
                (
                    "ChannelsId",
                    channel_id,
                )
            )

        dados = self.executar_get(
            (
                f"{self.chat_url}"
                "/v2/session"
            ),
            parametros,
        )

        if not isinstance(
            dados,
            dict,
        ):
            raise RuntimeError(
                "O retorno das sessões "
                "não é um objeto JSON."
            )

        if "items" not in dados:
            raise RuntimeError(
                "O retorno da API não "
                "contém o campo items."
            )

        return dados

    def obter_contato(
        self,
        contact_id: str,
    ) -> dict[str, Any]:
        parametros: list[
            tuple[str, str | int]
        ] = [
            (
                "IncludeDetails",
                "Tags",
            ),
            (
                "IncludeDetails",
                "Portfolios",
            ),
            (
                "IncludeDetails",
                "CustomFields",
            ),
        ]

        dados = self.executar_get(
            (
                f"{self.core_url}"
                f"/v1/contact/{contact_id}"
            ),
            parametros,
        )

        if not isinstance(
            dados,
            dict,
        ):
            raise RuntimeError(
                "O retorno do contato "
                "não é um objeto JSON."
            )

        return dados

    def listar_mensagens_pagina(
        self,
        session_id: str,
        pagina: int = 1,
    ) -> dict[str, Any]:
        data_inicial, data_final = (
            self.calcular_periodo()
        )

        parametros: list[
            tuple[str, str | int]
        ] = [
            (
                "CreatedAt.After",
                self.formatar_data(
                    data_inicial
                ),
            ),
            (
                "CreatedAt.Before",
                self.formatar_data(
                    data_final
                ),
            ),
            (
                "PageNumber",
                pagina,
            ),
            (
                "PageSize",
                PAGE_SIZE,
            ),
            (
                "OrderBy",
                "CreatedAt",
            ),
            (
                "OrderDirection",
                "ASCENDING",
            ),
        ]

        dados = self.executar_get(
            (
                f"{self.chat_url}"
                f"/v1/session/{session_id}"
                "/message"
            ),
            parametros,
        )

        if not isinstance(
            dados,
            dict,
        ):
            raise RuntimeError(
                "O retorno das mensagens "
                "não é um objeto JSON."
            )

        if "items" not in dados:
            raise RuntimeError(
                "O retorno das mensagens "
                "não contém items."
            )

        return dados

    def fechar(
        self,
    ) -> None:
        self.http.close()
