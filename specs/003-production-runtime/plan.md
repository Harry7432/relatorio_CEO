# Implementation Plan: Base de runtime de producao

**Branch**: `003-production-runtime` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-production-runtime/spec.md`

## Summary

Empacotar o projeto em uma unica imagem Python reproduzivel e executa-la no Coolify como processos
isolados de API, worker e frontend. A API FastAPI tera apenas `/health` e `/ready`, sem OpenAPI ou
interfaces de negocio; readiness fara uma consulta minima ao PostgreSQL sem divulgar diagnosticos.
O worker permanecera um job finito iniciado exclusivamente por `python -m src.sync_service` dentro
de um runner dedicado, e o Streamlit atual continuara disponivel. O desenho nao altera schema,
migrations, consultas, ordem de etapas ou regras de persistencia; apenas superficies de erro que
possam expor dados serao sanitizadas. A ativacao produtiva do worker depende da protecao de
concorrencia definida pela feature 002.

## Technical Context

**Language/Version**: Python 3.13.14, fixado na imagem de producao e no ambiente usado para gerar os locks

**Primary Dependencies**: FastAPI e Uvicorn para probes; psycopg 3 para readiness; Streamlit,
pandas, Plotly, requests, python-dotenv e openpyxl existentes; pip-tools somente para gerar locks

**Storage**: PostgreSQL existente como fonte de verdade; readiness executa apenas uma consulta de
conectividade; nenhuma alteracao de schema ou migration

**Testing**: pytest, FastAPI/Starlette TestClient, testes de contrato sem banco, integracao com
PostgreSQL descartavel e smoke tests da imagem/Compose

**Target Platform**: Containers Linux `linux/amd64` executados no Coolify por Docker Compose;
arquiteturas adicionais exigem locks e validacao proprios

**Project Type**: Aplicacao Python unica empacotada uma vez e iniciada em tres papeis de processo

**Performance Goals**: Health responde em ate 1 segundo no p95 sem I/O externo; readiness conclui em
ate 5 segundos; cada processo inicia ou falha explicitamente em ate 30 segundos, exceto o trabalho
de sincronizacao executado pelo worker

**Constraints**: Expor somente `/health` e `/ready`; desabilitar redirects, docs e OpenAPI; manter
`python -m src.sync_service`; nao iniciar sincronizacao automaticamente; preservar Streamlit; usar
uma imagem comum; fixar dependencias transitivas e artefatos por hash; excluir segredos do contexto
de build e dos logs; nao alterar schema nem logica de sincronizacao; bloquear ativacao produtiva do
worker ate a feature 002 comprovar exclusao mutua

**Scale/Scope**: Tres papeis de processo, dois endpoints sem dados de negocio, uma imagem de
aplicacao e uma instancia inicial por processo; escalabilidade horizontal e React fora do escopo

## Hard Prerequisite

A feature 002 MUST estar implementada e validada, com exclusao mutua entre qualquer acionamento
manual e agendado, antes do deploy produtivo e antes do `converge` desta feature. Ate esse gate
passar, o runtime pode ser construido e validado somente em homologacao isolada. Nao existe excecao
temporaria aprovada para concorrencia sem protecao.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate

| Gate | Result | Evidence |
|------|--------|----------|
| Evolucao incremental | PASS | Uma imagem, um modulo de API e configuracao de runtime sao adicionados sem reestruturar dominio ou sincronizacao. |
| PostgreSQL como fonte de verdade | PASS | Readiness apenas confirma acesso ao PostgreSQL existente; nenhum armazenamento paralelo ou migration e criado. |
| Processos independentes | PASS | API, worker e Streamlit recebem comandos e ciclos de vida separados na mesma imagem. |
| Contrato estavel do worker | PASS | O comando publico permanece exatamente `python -m src.sync_service`. |
| Sincronizacao confiavel | PASS | O runner nao executa sincronizacao no deploy de homologacao; deploy produtivo e converge dependem da protecao de concorrencia da feature 002. |
| Seguranca e observabilidade | PASS | Segredos ficam fora do build; probes e superficies existentes de erro terao redacao testada sem mudar resultados de negocio. |
| Regras criticas verificadas | PASS | API, readiness, redacao, comandos, worker e Streamlit terao testes de contrato, caracterizacao e validacao ponta a ponta. |
| Streamlit preservado | PASS | O processo atual continua empacotado e executavel; React e retirada do Streamlit ficam fora do escopo. |
| Fluxo de entrega | PASS | A feature possui specify e plan; tasks, implement e converge permanecem como etapas posteriores. |

## Project Structure

### Documentation (this feature)

```text
specs/003-production-runtime/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── runtime-api.yaml
│   └── runtime-processes.md
└── tasks.md                 # Criado posteriormente por /speckit.tasks
```

### Source Code (repository root)

```text
.dockerignore                # Exclui segredos, ambientes locais e caches do build
.python-version              # Alinha o Python local com a imagem
Dockerfile                   # Imagem unica, base e dependencias fixadas
compose.yaml                 # API, worker-runner e frontend isolados
.env.example                 # Somente nomes e valores ficticios seguros
requirements.in              # Dependencias diretas de producao
requirements.txt             # Lock de producao transitivo com hashes
requirements-dev.in          # Dependencias diretas de validacao
requirements-dev.txt         # Lock de validacao transitivo com hashes
app.py                       # Frontend preservado; apresentacao de erros sanitizada
src/
├── api.py                   # FastAPI somente com health e readiness
├── botnext_client.py        # Erros HTTP sanitizados, sem alterar chamadas
├── database.py              # Acesso existente; sem mudanca de schema
├── config.py                # Configuracao existente, sem segredos versionados
├── runtime_security.py      # Redacao central de valores e excecoes sensiveis
├── sync_mensagens.py        # Saida operacional sem IDs ou conteudo sensivel
└── sync_service.py          # Ordem/resultado preservados; erros sanitizados
tests/
├── test_runtime_api.py      # Contrato dos probes, falhas e redacao
├── test_runtime_processes.py # Comandos, runner e independencia
├── test_runtime_security.py # Segredos sem resposta, log ou erro
├── test_sync_service.py     # Caracterizacao da ordem, subprocessos e main
├── test_streamlit_smoke.py  # Startup e fluxos sob dependencias controladas
└── test_seller_metrics.py   # Regressao existente
```

**Structure Decision**: Manter o projeto Python unico e criar uma imagem neutra compartilhada. O
`compose.yaml` inicia API, Streamlit e um `worker-runner` ocioso em containers separados. Coolify
executa `python -m src.sync_service` como tarefa dentro do runner, pois sua tarefa agendada exige um
container ativo e nao cria containers efemeros. O runner nunca sincroniza durante deploy; o
agendamento pertence a feature 002 e so pode ser ativado depois da exclusao mutua. A API fica em um
unico `src/api.py`, pois dois probes nao justificam nova camada. A redacao de erros e transversal,
mas nao altera chamadas, ordem, persistencia, idempotencia ou resultado de negocio da sincronizacao.

## Phase 0: Research

As decisoes e fontes estao consolidadas em [research.md](./research.md). Nao restam marcadores
`NEEDS CLARIFICATION` nem decisoes bloqueantes.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) define os estados operacionais sem criar entidades persistidas.
- [contracts/runtime-api.yaml](./contracts/runtime-api.yaml) fixa as duas operacoes HTTP e suas
  respostas minimas.
- [contracts/runtime-processes.md](./contracts/runtime-processes.md) fixa comandos, configuracao e
  semantica de ciclo de vida dos tres processos.
- [quickstart.md](./quickstart.md) descreve validacao dos locks, imagem, probes, processos,
  regressao de schema e ausencia de segredos.

### Post-Design Constitution Check

| Gate | Result | Design confirmation |
|------|--------|---------------------|
| Evolucao incremental | PASS | O desenho adiciona apenas arquivos de runtime, um modulo pequeno de API e testes focados. |
| PostgreSQL como fonte de verdade | PASS | O modelo nao persiste estado e o contrato de readiness usa somente uma consulta de conectividade. |
| Processos independentes | PASS | O contrato define um container e um comando por papel, sem supervisor compartilhado. |
| Contrato estavel do worker | PASS | O contrato de processo preserva literalmente `python -m src.sync_service`. |
| Sincronizacao confiavel | PASS | Runner ocioso evita execucao implicita; deploy e converge permanecem bloqueados ate a feature 002 validar exclusao mutua em todos os acionamentos. |
| Seguranca e observabilidade | PASS | Contratos omitem detalhes; `.dockerignore`, exemplos ficticios, redacao de erros e testes com segredos semeados sao obrigatorios. |
| Regras criticas verificadas | PASS | Quickstart e testes cobrem API exata, builds duplos, worker caracterizado, Streamlit, isolamento, schema e redacao. |
| Streamlit preservado | PASS | O comando Streamlit e parte do contrato e usa a mesma imagem, sem substituicao por React. |
| Fluxo de entrega | PASS | Os artefatos de plan estao completos e deixam implementacao para tasks/implement. |

## Complexity Tracking

Nenhuma violacao constitucional ou complexidade excepcional requer justificativa.
