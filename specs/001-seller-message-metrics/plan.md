# Implementation Plan: Metricas de utilizacao por vendedor

**Branch**: `001-seller-message-metrics` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-seller-message-metrics/spec.md`

## Summary

Adicionar a aba existente de vendedores uma metrica dedicada ao volume de mensagens efetivamente enviadas por vendedor, com total geral, ranking e participacao percentual. A implementacao reutilizara os filtros atuais de periodo e canal e os dados ja carregados do PostgreSQL, filtrara mensagens `TO_HUB` com usuario remetente presente, eliminara duplicidades por `mensagem_id` e agrupara pela identificacao existente em `vendedor_responsavel`. A regra de agregacao ficara em uma funcao pura e testavel; sincronizacao, regras de identificacao e schema permanecerao inalterados.

## Technical Context

**Language/Version**: Python 3.13.14

**Primary Dependencies**: Streamlit 1.62.0, pandas 3.0.5, Plotly 7.0.0, psycopg 3.3.4

**Storage**: PostgreSQL existente, com leitura das tabelas `mensagens`, `sessoes`, `contatos` e `usuarios_botnext`; nenhuma alteracao de schema

**Testing**: pytest para testes unitarios da agregacao; validacao manual do fluxo Streamlit conforme `quickstart.md`

**Target Platform**: Aplicacao web Streamlit no ambiente atual do projeto

**Project Type**: Dashboard web Python de projeto unico

**Performance Goals**: Atualizar total, ranking e percentuais em ate 5 segundos apos mudanca valida de periodo ou canal no volume operacional normal

**Constraints**: Preservar arquitetura e sincronizacao; consumir somente dados persistidos; nao alterar regras de identificacao; excluir recebidas e automacoes; deduplicar por mensagem; manter `Não identificado`; nao registrar conteudo ou dados sensiveis

**Scale/Scope**: Uma nova secao na aba `Vendedores`, processando o dataframe de mensagens ja carregado e armazenado em cache; volume atual na ordem de milhares de mensagens

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

A constituicao em `.specify/memory/constitution.md` ainda contem apenas placeholders e nao define gates ratificados. Foram aplicados os principios obrigatorios informados para o projeto e as orientacoes de `AGENTS.md`.

### Pre-Design Gate

| Gate | Result | Evidence |
|------|--------|----------|
| Preservar arquitetura e evoluir incrementalmente | PASS | A solucao reutiliza `app.py`, `buscar_dados_dashboard()` e os filtros existentes; adiciona somente uma funcao de regra de negocio testavel. |
| PostgreSQL como fonte persistente | PASS | A metrica consome as tabelas ja sincronizadas; nao cria armazenamento paralelo nem migration. |
| Nao alterar sincronizacao sem necessidade | PASS | Nenhum arquivo `sync_*`, cliente BotNext ou repositorio de escrita faz parte do desenho. |
| Identificacao de vendedor separada da persistencia | PASS | A metrica consome `vendedor_responsavel` ja calculado e nao modifica `vendedor_service.py`. |
| Idempotencia e ausencia de duplicidade | PASS | A leitura elimina repeticoes logicas por `mensagem_id`; a persistencia existente continua inalterada. |
| Novas regras criticas testaveis | PASS | Elegibilidade, deduplicacao, agrupamento, percentuais e ordenacao serao cobertos por testes pytest de funcao pura. |
| Seguranca e observabilidade | PASS | Nenhuma credencial, payload ou conteudo de mensagem sera adicionado a logs ou artefatos. Erros de integridade da metrica nao serao ignorados silenciosamente. |
| Escopo minimo | PASS | Sem nova API, framework, servico, schema, grafico ou refatoracao ampla. |

## Project Structure

### Documentation (this feature)

```text
specs/001-seller-message-metrics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dashboard-ui.md
└── tasks.md                 # Criado posteriormente por /speckit.tasks
```

### Source Code (repository root)

```text
app.py                       # Filtros e apresentacao Streamlit existentes
src/
├── dashboard_repository.py  # Projecao de leitura das mensagens persistidas
├── seller_metrics.py        # Nova funcao pura de agregacao
└── vendedor_service.py      # Regra existente, sem alteracao
tests/
└── test_seller_metrics.py   # Testes unitarios da regra de negocio
requirements.txt             # Inclusao de pytest se adotado como manifesto unico
```

**Structure Decision**: Manter o projeto unico atual. A UI continua em `app.py`; apenas a regra de agregacao sera extraida para `src/seller_metrics.py` porque possui regras criticas independentes e precisa ser testada sem executar o Streamlit ou acessar o banco. `dashboard_repository.py` recebera somente a projecao do identificador de usuario da mensagem, se necessario para distinguir envio humano de automacao.

## Phase 0: Research

As decisoes, evidencias e alternativas estao consolidadas em [research.md](./research.md). Nao restaram pendencias de pesquisa ou decisoes tecnicas em aberto.

## Phase 1: Design & Contracts

- [data-model.md](./data-model.md) define a projecao de mensagem, a selecao de analise e o resultado agregado sem criar novas tabelas.
- [contracts/dashboard-ui.md](./contracts/dashboard-ui.md) define os filtros que afetam a metrica, os resultados, os estados vazio e invalido e as regras de atribuicao.
- [quickstart.md](./quickstart.md) descreve testes automatizados e validacao manual ponta a ponta.

### Post-Design Constitution Check

| Gate | Result | Design confirmation |
|------|--------|---------------------|
| Arquitetura incremental | PASS | Um modulo puro e uma integracao localizada na aba existente. |
| Persistencia explicita | PASS | Nenhuma tabela, coluna ou migration nova. |
| Sincronizacao preservada | PASS | Todo o desenho inicia nos dados retornados pela consulta existente. |
| Regra de vendedor preservada | PASS | Agrupamento usa `vendedor_responsavel`; `usuario_id_mensagem` serve apenas para comprovar envio humano. |
| Duplicidade controlada | PASS | Identidade logica unica por `mensagem_id` antes do agrupamento. |
| Testabilidade | PASS | Contrato deterministico e casos de teste descritos no quickstart. |
| Seguranca | PASS | Saida contem somente nome do vendedor e metricas agregadas; nenhum conteudo de mensagem. |
| Escopo | PASS | Contratos limitados ao dashboard interno; nenhuma interface externa nova. |

## Complexity Tracking

Nenhuma violacao ou complexidade adicional requer justificativa.
