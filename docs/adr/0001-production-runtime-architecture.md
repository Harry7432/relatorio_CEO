# [ADR-0001] Imagem Única Reproduzível e Separação de Papéis de Runtime

* **Status**: Aceito
* **Data**: 2026-09-24
* **Autores**: Equipe de Arquitetura

## Contexto e Problema

O projeto `relatorio_CEO` é composto por um dashboard visual (Streamlit), probes HTTP de liveness e readiness (FastAPI) e um worker de sincronização incremental (Python). Era necessário garantir um ambiente de produção empacotado de forma reproduzível, sem duplicar dependências ou vazamentos de credenciais.

## Decisão Considerada

Adotar uma única imagem Docker neutra e imutável baseada em Python `3.13.14-slim` com dependências travadas por hash (`requirements.txt`), executada sob usuário não-root (`USER app`). 
A composição em `compose.yaml` deriva os três papéis operacionais (`api`, `worker`, `frontend`) a partir desse mesmo artefato de imagem, mantendo os seus ciclos de vida independentes.

## Consequências

### Positivas
* **Garantia de Reproduzibilidade**: builds idênticos produzem inventários exatos de pacotes e hashes.
* **Segurança e Isolamento**: execução não-root sem vazamento de arquivos locais ou segredos no contexto de build.
* **Desacoplamento de Processos**: falhas ou reinícios em um papel não afetam os demais containers.

### Negativas ou Riscos
* Exige sincronia de variáveis de build (`SOURCE_REVISION`, `DEPENDENCY_LOCK_DIGEST`).
* O worker de produção exige portão de controle (Feature 002) para exclusão mútua antes de ser ativado em cron/agendamento.
